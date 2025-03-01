import sqlite3
import csv
import datetime
from pathlib import Path

DB_PATH = "reviews.db"
EXPORT_DIR = "exports"

def format_date(date_str):
    """
    Convert ISO format date string like '2025-01-14T00:14:30Z' 
    into a human readable format "Jan 14, 2025 00:14:30"
    """
    if not date_str:
        return ""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str

def export_to_csv():
    # Create exports directory if it doesn't exist
    Path(EXPORT_DIR).mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{EXPORT_DIR}/reviews_export_{timestamp}.csv"
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all column names
    cursor.execute("PRAGMA table_info(reviews)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Fetch all reviews
    cursor.execute("""
        SELECT 
            id,
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
        FROM reviews
        ORDER BY date DESC
    """)
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(columns)
        
        # Write data rows with date formatting
        total_rows = 0
        for row in cursor:
            # Convert row to list for modification
            row_list = list(row)
            
            # Format dates (date and developer_reply_date are at indices 4 and 14)
            row_list[4] = format_date(row_list[4])
            row_list[14] = format_date(row_list[14])
            
            writer.writerow(row_list)
            total_rows += 1
            
            # Print progress every 10000 rows
            if total_rows % 10000 == 0:
                print(f"Exported {total_rows} rows...")
    
    conn.close()
    
    print(f"\nExport complete!")
    print(f"Total rows exported: {total_rows}")
    print(f"File saved as: {filename}")
    
    # Print file size
    file_size = Path(filename).stat().st_size
    size_mb = file_size / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")

if __name__ == "__main__":
    print("Starting export...")
    export_to_csv() 