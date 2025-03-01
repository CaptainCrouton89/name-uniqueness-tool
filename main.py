import asyncio
import json
import re
from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp
import requests

# Define API key and endpoint
API_KEY = "gJSVqIZAIgdYBm1gYkNmrqUtavM"
URL = "https://public-api.apptweak.com/api/public/store/apps/reviews/top-displayed.json?apps=835599320&sort=most_useful&country=us&language=us&device=iphone&limit=10&offset=0"

async def fetch_app_reviews():
    headers = {
        'accept': 'application/json',
        'x-apptweak-key': API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=headers) as response:
            response.raise_for_status()  # will raise an exception for error status codes
            data = await response.json()
            # Save the JSON data to a file
            with open('reviews.json', 'w') as file:
                json.dump(data, file, indent=4)
            print("Data saved to reviews.json")
            print(data)
            return data

async def fetch_recent_reviews_by_url(app_url: str):
    """
    Extracts the app ID from an App Store or Play Store URL, constructs the API URL with sort=most_recent,
    fetches the recent reviews, saves to a file, and prints the data.
    """
    if "play.google.com" in app_url:
        # For Play Store: extract the package name from the query parameter "id"
        store = "playstore"
        device = "android"
        sort = "most_recent"
        parsed_url = urlparse(app_url)
        qs = parse_qs(parsed_url.query)
        if "id" in qs:
            app_id = qs["id"][0]
        else:
            raise ValueError("Invalid Play Store URL: missing 'id' parameter")
    elif "apps.apple.com" in app_url:
        # For App Store: extract numeric id from the path after "/id"
        store = "appstore"
        device = "iphone"
        sort = "most_recent"
        tokens = app_url.split("/id")
        if len(tokens) >= 2:
            id_part = tokens[1]
            match = re.match(r"(\d+)", id_part)
            if match:
                app_id = match.group(1)
            else:
                raise ValueError("Invalid App Store URL: No numeric id found")
        else:
            raise ValueError("Invalid App Store URL")
    else:
        raise ValueError("URL is not recognized as a Play Store or App Store URL")

    # Construct the API URL with the extracted app_id and required query parameters
    endpoint = "https://public-api.apptweak.com/api/public/store/apps/reviews/top-displayed.json"
    query_params = {
         'apps': app_id,
         'sort': sort,
         'country': 'us',
         'language': 'us',
         'device': device,
         'limit': 10,
         'offset': 0
    }
    api_url = f"{endpoint}?{urlencode(query_params)}"

    headers = {
         'accept': 'application/json',
         'x-apptweak-key': API_KEY
    }
    async with aiohttp.ClientSession() as session:
         async with session.get(api_url, headers=headers) as response:
             response.raise_for_status()
             data = await response.json()
             filename = f"recent_reviews_{app_id}.json"
             with open(filename, 'w') as file:
                 json.dump(data, file, indent=4)
             print(f"Recent reviews saved to {filename}")
             print(data)
             return data

async def main():
    # print("Fetching top displayed reviews:")
    # await fetch_app_reviews()

    # print("\nFetching recent reviews from provided URL:")
    # Sample Play Store URL for testing; replace with any valid App Store or Play Store URL
    test_url = "https://play.google.com/store/apps/details?id=com.draftkings.sportsbook"
    await fetch_recent_reviews_by_url(test_url)

if __name__ == "__main__":
    asyncio.run(main())