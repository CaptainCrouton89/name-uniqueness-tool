import csv
import glob
import os
import re
import sqlite3
import time

from NameUniquenessScorer import NameUniquenessScorer


def is_valid_name(name):
    """Check if a name appears to be a valid human name."""
    # Check for numbers
    if re.search(r'\d', name):
        return False
    
    # Check for unusual characters that aren't typically in names
    if re.search(r'[@#$%^&*+=<>{}[\]|/]', name):
        return False
    
    # Check for usernames, handles, or other non-name patterns
    if re.search(r'^\w+\d+$', name) or name.count('_') > 0:
        return False
    
    suffixes = ['mr.', 'mr', 'sr.', 'sr', 'jr.', 'jr', 'dr.', 'dr', 'ms.', 'ms', 'mrs.', 'mrs', 'inc', 'llc', 'ltd', 'co', 'corp', 'gaming', 'official', 'real', 'the', 'channel', 'tv', 'yt', 'youtube', 'video', 'videos', 'gram', 'ig', 'insta', 'fb', 'tweet', 'tiktok', 'live', 'gaming', 'plays', 'stream']
    name_lower = name.lower()
    name_parts = name_lower.split()
    for suffix in suffixes:
        if suffix in name_parts:
            return False
        
    # Check that name has both first and last name
    name_parts = name.split()
    if len(name_parts) < 2:
        return False
        
    # Check for single letter names
    if len(name_parts[0]) == 1 or len(name_parts[-1]) == 1:
        return False
    
    # All-caps names will be converted to title case later, not rejected
    
    return True


def simplify_name(author_name):
    """
    Simplify a name to just first and last name with proper capitalization.
    Returns a tuple of (first_name, last_name, is_valid)
    """
    # Check if the name is valid
    if not is_valid_name(author_name):
        # Try to extract a valid name if possible
        parts = re.split(r'[^a-zA-Z\s\'-]', author_name)
        clean_parts = [p.strip() for p in parts if p.strip()]
        if not clean_parts:
            return ("", "", False)
        author_name = " ".join(clean_parts)
        if not is_valid_name(author_name):
            return ("", "", False)
        
    
    
    # Convert all-caps names to title case
    author_name = author_name.title()
    
    # Split the name into parts
    parts = author_name.split()
    
    # Handle single-word names
    if len(parts) == 1:
        return (parts[0].title(), "", True)
    
    # For multi-word names, take first and last parts
    first_name = parts[0].title()
    last_name = parts[-1].title()

    # Check if the name exists in the dataset
    if not scorer.name_exists(first_name, "first") and not scorer.name_exists(last_name, "last"):
        return ("", "", False)
    
    # Handle special cases like "John D." where the last part is just an initial
    if len(parts) > 1 and (len(parts[-1]) == 1 or (len(parts[-1]) == 2 and parts[-1].endswith('.'))):
        # If the last part is just an initial, use the part before it as the last name
        if len(parts) > 2:
            last_name = parts[-2].title()
        else:
            last_name = ""
    
    return (first_name, last_name, True)


def score_review_authors(batch_size=100):
    start_time = time.time()
    
    # Initialize the name scorer
    print("Initializing name scorer...")
    global scorer
    scorer = NameUniquenessScorer("./name_data")
    
    # Connect to the SQLite database
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()
    
    # Get all unique author names from the reviews table along with their review details
    cursor.execute("""
        SELECT DISTINCT author_name, 
               rating, title, date, review_id, app_id, body
        FROM reviews 
        WHERE author_name IS NOT NULL AND author_name != ''
    """)
    author_data = cursor.fetchall()
    
    # Create a dictionary to store review details for each author
    author_reviews = {}
    for row in author_data:
        author_name = row[0]
        review_details = row[1:]  # rating, title, date, review_id, app_id, body
        
        if author_name not in author_reviews:
            author_reviews[author_name] = review_details
    
    author_names = list(author_reviews.keys())
    total_names = len(author_names)
    print(f"Found {total_names} unique author names to score")
    
    # Process in batches to show progress
    scored_authors = []
    valid_count = 0
    invalid_count = 0
    
    for i in range(0, total_names, batch_size):
        batch = author_names[i:i+batch_size]
        batch_scores = []
        
        for author_name in batch:
            # Simplify the name
            first_name, last_name, is_valid = simplify_name(author_name)
            
            if is_valid:
                # Score valid names
                if last_name:
                    score = scorer.calculate_full_name_uniqueness(first_name, last_name)
                else:
                    score = scorer.calculate_first_name_uniqueness(first_name) / 2
                valid_count += 1
            else:
                # Invalid names get a score of -1
                score = -1
                invalid_count += 1
            
            # Get the review details for this author
            review_details = author_reviews[author_name]
            rating, title, date, review_id, app_id, body = review_details
            
            # Append all data to the batch scores
            batch_scores.append((author_name, first_name, last_name, score, rating, title, date, review_id, app_id, body))
        
        scored_authors.extend(batch_scores)
        
        # Report progress
        progress = min(100, round((i + len(batch)) / total_names * 100, 1))
        elapsed = time.time() - start_time
        names_per_second = (i + len(batch)) / elapsed if elapsed > 0 else 0
        eta_seconds = (total_names - (i + len(batch))) / names_per_second if names_per_second > 0 else 0
        eta_minutes = eta_seconds / 60
        
        print(f"Progress: {progress}% ({i + len(batch)}/{total_names}) | "
              f"Speed: {names_per_second:.1f} names/sec | "
              f"ETA: {eta_minutes:.1f} minutes")
        
        # Save intermediate results every 1000 names
        if (i + len(batch)) % 1000 == 0 or (i + len(batch)) == total_names:
            # Sort by score in descending order (but put -1 scores at the end)
            temp_sorted = sorted(scored_authors, key=lambda x: (x[3] == -1, -x[3]))
            
            # Save intermediate results to CSV
            with open(f"simplified_name_scores_partial_{i + len(batch)}.csv", "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Original Name", "First Name", "Last Name", "Uniqueness Score", 
                                "Rating", "Title", "Date", "Review ID", "App ID", "Body"])
                for author in temp_sorted:
                    writer.writerow(author)
            
            print(f"Saved intermediate results to simplified_name_scores_partial_{i + len(batch)}.csv")
    
    # Sort by score in descending order (but put -1 scores at the end)
    scored_authors.sort(key=lambda x: (x[3] == -1, -x[3]))
    
    # Save final results to CSV
    with open("simplified_name_scores.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original Name", "First Name", "Last Name", "Uniqueness Score", 
                        "Rating", "Title", "Date", "Review ID", "App ID", "Body"])
        for author in scored_authors:
            writer.writerow(author)
    
    # Print top 10 most unique valid names
    print("\nTop 10 Most Unique Valid Names:")
    valid_names = [a for a in scored_authors if a[3] != -1]
    for i, (original, first, last, score, rating, title, date, review_id, app_id, body) in enumerate(valid_names[:10], 1):
        full_name = f"{first} {last}".strip()
        print(f"{i}. {full_name}: {score:.1f} (Original: {original})")
    
    # Print statistics
    print(f"\nTotal names processed: {total_names}")
    print(f"Valid names: {valid_count} ({valid_count/total_names*100:.1f}%)")
    print(f"Invalid names: {invalid_count} ({invalid_count/total_names*100:.1f}%)")
    
    conn.close()
    
    total_time = time.time() - start_time
    print(f"\nScored {len(scored_authors)} author names in {total_time:.1f} seconds")
    print(f"Results saved to simplified_name_scores.csv")
    # Remove all partial save files
    for filename in glob.glob("simplified_name_scores_partial_*.csv"):
        try:
            os.remove(filename)
            print(f"Removed partial results file: {filename}")
        except OSError as e:
            print(f"Error removing {filename}: {e}")

if __name__ == "__main__":
    score_review_authors(batch_size=100)