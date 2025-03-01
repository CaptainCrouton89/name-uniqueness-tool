import asyncio
import datetime
import sqlite3
from urllib.parse import urlencode

import aiohttp

# Reference: https://developers.apptweak.com/reference/app-reviews-search
# This script is designed to fetch reviews from the Play Store using AppTweak's API Search endpoint
# and insert them into an SQLite database. It tracks which offset has been fetched so you can
# resume from the last position if the script is interrupted.

API_KEY = "gJSVqIZAIgdYBm1gYkNmrqUtavM"
DB_PATH = "reviews.db"

# For now, just one Play Store app as requested. Additional apps can be added to this list.
PLAYSTORE_APPS = [
    "com.compositest.fortunescratchlife",
    "com.playtowin.playtowin",
    "com.lobstermania.slots",
    "com.productmadness.cashmancasino",
    "com.sciplay.quickhit",
    "com.joyvo.casinohouse",
    "com.huuuge.casino.texas",
    "com.lotsaslots.casino",
    "com.jackpot.world.casino",
    "com.gamehausnetwork.grandcashcasino",
    "com.playstudios.popslots",
]


def init_db():
    """
    Create or verify the required tables:
      - reviews: to store the fetched reviews
      - scrape_state: to keep track of where we left off (offset) for each app
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT,
            review_id TEXT UNIQUE,
            rating INTEGER,
            date TEXT,
            language TEXT,
            author_name TEXT,
            author_photo TEXT,
            author_profile TEXT,
            title TEXT,
            body TEXT,
            body_length INTEGER,
            version TEXT,
            developer_reply TEXT,
            developer_reply_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrape_state (
            app_id TEXT PRIMARY KEY,
            last_offset INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def get_scrape_offset(app_id: str) -> int:
    """
    Retrieve the last offset scraped for a given app_id from the scrape_state table.
    Returns 0 if there's no record.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT last_offset FROM scrape_state WHERE app_id = ?",
        (app_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0


def set_scrape_offset(app_id: str, offset: int):
    """
    Update or insert the last offset for a given app_id into the scrape_state table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scrape_state (app_id, last_offset) 
        VALUES (?, ?)
        ON CONFLICT(app_id) DO UPDATE SET last_offset=excluded.last_offset
    """, (app_id, offset))

    conn.commit()
    conn.close()


async def fetch_review_page(session, app_id: str, offset: int, limit: int = 100) -> int:
    """
    Fetch a single page of reviews using the search endpoint, store them in the DB,
    and return how many reviews were inserted.
    """
    endpoint = "https://public-api.apptweak.com/api/public/store/apps/reviews/search.json"
    params = {
        "apps": app_id,
        "country": "us",
        "language": "us",
        "device": "android",
        "limit": limit,
        "offset": offset,
        "sort": "most_recent",
        "start_date": "2016-01-01",
        "end_date": datetime.date.today().strftime("%Y-%m-%d")
    }
    url = f"{endpoint}?{urlencode(params)}"

    headers = {
        "accept": "application/json",
        "x-apptweak-key": API_KEY
    }

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        data = await response.json()

    reviews_by_app = data.get("result", {}).get(app_id, {})
    reviews_data = reviews_by_app.get("reviews", [])

    if not reviews_data:
        return 0

    # Insert reviews into the SQLite DB, skipping duplicates via UNIQUE(review_id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for review in reviews_data:
        cursor.execute("""
            INSERT OR IGNORE INTO reviews (
                app_id,
                review_id,
                rating,
                date,
                language,
                author_name,
                author_photo,
                author_profile,
                title,
                body,
                body_length,
                version,
                developer_reply,
                developer_reply_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app_id,
            review.get("id"),
            review.get("rating"),
            review.get("date"),
            review.get("language", ""),
            review.get("author", {}).get("name", ""),
            review.get("author", {}).get("photo", ""),
            review.get("author", {}).get("profile", ""),
            review.get("title", ""),
            review.get("body", ""),
            review.get("body_length", 0),
            review.get("version", ""),
            review.get("developer_reply"),
            review.get("developer_reply_date")
        ))
    conn.commit()
    conn.close()

    return len(reviews_data)


async def main():
    init_db()  # Ensure our database is ready
    
    async with aiohttp.ClientSession() as session:
        for app_id in PLAYSTORE_APPS:
            offset = get_scrape_offset(app_id)
            total_fetched = 0
            max_reviews = 500000  # We'll stop once we've reached 100,000 reviews for that app
            
            while total_fetched < max_reviews:
                # Fetch one page
                inserted_count = await fetch_review_page(session, app_id, offset, limit=100)
                print(f"Offset={offset}, Inserted {inserted_count} reviews for {app_id}")
                
                if inserted_count == 0:
                    print(f"No more reviews for {app_id}. Stopping.")
                    break
                
                # We inserted 'inserted_count' new reviews
                total_fetched += inserted_count
                offset += 100
                
                # Update DB record for offset so if we are interrupted, we can resume later
                set_scrape_offset(app_id, offset)

                if total_fetched >= max_reviews:
                    print(f"Reached {max_reviews} reviews, stopping for {app_id}.")
                    break


if __name__ == "__main__":
    asyncio.run(main()) 