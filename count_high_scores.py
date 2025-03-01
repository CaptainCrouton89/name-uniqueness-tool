import csv


def count_high_scores(threshold=50):
    """
    Count how many names in the simplified_name_scores.csv file have a uniqueness score over the threshold.
    
    Args:
        threshold (float): The score threshold to count (default: 50)
        
    Returns:
        int: The count of names with scores over the threshold
    """
    high_score_count = 0
    valid_name_count = 0
    score_ranges = {
        "0-10": 0,
        "10-20": 0,
        "20-30": 0,
        "30-40": 0,
        "40-50": 0,
        "50-60": 0,
        "60-70": 0,
        "70-80": 0,
        "80-90": 0,
        "90-100": 0
    }
    
    print("Starting to process the CSV file...")
    
    try:
        with open('simplified_name_scores.csv', 'r', newline='', encoding='utf-8') as csvfile:
            print("File opened successfully")
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip header row
            print(f"Header: {header}")
            
            # Find the index of the score column
            score_index = 3  # Default position based on the file we examined
            print(f"Using score index: {score_index}")
            
            row_count = 0
            for row in reader:
                row_count += 1
                if row_count % 10000 == 0:
                    print(f"Processed {row_count} rows...")
                
                if len(row) > score_index:  # Ensure we have enough columns
                    try:
                        score = float(row[score_index])
                        if score != -1:  # Count only valid names
                            valid_name_count += 1
                            
                            # Categorize scores into ranges
                            if 0 <= score < 10:
                                score_ranges["0-10"] += 1
                            elif 10 <= score < 20:
                                score_ranges["10-20"] += 1
                            elif 20 <= score < 30:
                                score_ranges["20-30"] += 1
                            elif 30 <= score < 40:
                                score_ranges["30-40"] += 1
                            elif 40 <= score < 50:
                                score_ranges["40-50"] += 1
                            elif 50 <= score < 60:
                                score_ranges["50-60"] += 1
                            elif 60 <= score < 70:
                                score_ranges["60-70"] += 1
                            elif 70 <= score < 80:
                                score_ranges["70-80"] += 1
                            elif 80 <= score < 90:
                                score_ranges["80-90"] += 1
                            elif 90 <= score <= 100:
                                score_ranges["90-100"] += 1
                            
                            if score > threshold:
                                high_score_count += 1
                    except ValueError as e:
                        print(f"Error parsing score in row {row_count}: {e}")
                        print(f"Row data: {row}")
                        # Skip rows with non-numeric scores
                        if row_count < 10:  # Only print first few errors
                            pass
                else:
                    if row_count < 10:  # Only print first few errors
                        print(f"Row {row_count} has insufficient columns: {row}")
    
        print(f"\nTotal rows processed: {row_count}")
        print(f"Total valid names: {valid_name_count}")
        print(f"Names with uniqueness score > {threshold}: {high_score_count}")
        print(f"Percentage: {(high_score_count/valid_name_count*100) if valid_name_count > 0 else 0:.2f}%")
        
        print("\nScore distribution:")
        for range_name, count in score_ranges.items():
            percentage = (count/valid_name_count*100) if valid_name_count > 0 else 0
            print(f"{range_name}: {count} names ({percentage:.2f}%)")
        
        return high_score_count
    
    except FileNotFoundError:
        print("Error: simplified_name_scores.csv file not found.")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0

if __name__ == "__main__":
    count_high_scores(50) 