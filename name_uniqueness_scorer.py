import csv
import math
import os
import re
from collections import Counter, defaultdict
from io import StringIO


class NameUniquenessScorer:
    def __init__(self, first_name_dir=None, last_name_source=None, custom_weights=None):
        # Default weights configuration
        self.weights = {
            # Component weights (should sum to 100)
            "frequency_weight": 80,
            "structural_weight": 10,
            "letter_dist_weight": 10,
            
            # Frequency score parameters
            "unknown_name_base_score": 100,
            "bigram_rarity_multiplier": 15,
            
            # Frequency thresholds and scores
            "very_rare_threshold": 0.0005,
            "very_rare_base_score": 40,
            "very_rare_bonus_max": 20,
            
            "uncommon_threshold": 0.001,
            "uncommon_base_score": 20,
            "uncommon_bonus_max": 10,
            
            "moderate_threshold": 0.005,
            "moderate_base_score": 10,
            "moderate_bonus_max": 5,
            
            "common_threshold": 0.01,
            "common_base_score": 5,
            "common_bonus_max": 5,
            
            "very_common_max_score": 5,
            "very_common_scale_factor": 0.2,
            
            # Structural score parameters
            "length_factor_weight": 0.6,
            "unusual_chars_weight": 0.4,
            "max_name_length": 12,
            "max_unusual_chars": 2,
            
            # Full name combination parameters
            "first_name_weight": 0.6,
            "last_name_weight": 0.4,
            "rare_combo_threshold": 70,
            "rare_combo_bonus": 20,
            "common_combo_threshold": 40,
            "common_combo_divisor": 20,
        }
        
        # Override default weights with custom weights if provided
        if custom_weights and isinstance(custom_weights, dict):
            for key, value in custom_weights.items():
                if key in self.weights:
                    self.weights[key] = value
        
        # Initialize counters
        self.first_name_counts = Counter()
        self.last_name_counts = Counter()
        self.total_first_names = 0
        self.total_last_names = 0
        self.letter_counts = Counter()
        
        # Load first name data if directory provided
        if first_name_dir:
            self.load_ssa_data(first_name_dir)
        
        # Load last name data
        if last_name_source:
            self.load_last_name_data(last_name_source)
        else:
            self.load_census_last_names()
    
    def load_ssa_data(self, directory_path):
        """Load SSA baby name data from yobYYYY.txt files"""
        pattern = re.compile(r'yob(\d{4})\.txt')
        # Only process files from 1950 onwards
        min_year = 1950
        year_data = {}
        
        for filename in os.listdir(directory_path):
            match = pattern.match(filename)
            if match and int(match.group(1)) < min_year:
                continue
            if match:
                year = match.group(1)
                year_data[year] = []
                
                with open(os.path.join(directory_path, filename), 'r') as file:
                    for line in file:
                        name, sex, count = line.strip().split(',')
                        count = int(count)
                        self.first_name_counts[name.title()] += count
                        self.total_first_names += count
                        self.letter_counts.update(name.lower())
        
        print(f"Loaded first name data: {len(self.first_name_counts)} unique names, {self.total_first_names} total")
    
    def load_census_last_names(self):
        """Load US Census Bureau last name data"""
        try:
            print("Loading census last name data...")
            with open('name_data/last_names.csv', 'r') as file:
                next(file) # Skip header line
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        if len(parts) >= 3:
                            name,rank,count,prop100k,cum_prop100k,pctwhite,pctblack,pctapi,pctaian,pct2prace,pcthispanic = parts
                            count = int(float(count))
                            self.last_name_counts[name.title()] += count
                            self.total_last_names += count
            print(f"Loaded last name data: {len(self.last_name_counts)} unique surnames, {self.total_last_names} total")
        
        except Exception as e:
            print(f"Error loading census data: {e}")
            # Fallback to minimal dataset
            self.last_name_counts = Counter({
                "SMITH": 2442977, "JOHNSON": 1932812, "WILLIAMS": 1625252,
                "BROWN": 1437026, "JONES": 1425470, "GARCIA": 1166120
            })
            self.total_last_names = sum(self.last_name_counts.values())
    
    def load_last_name_data(self, source_path):
        """Load custom last name data"""
        try:
            with open(source_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 2:
                        name, count = row[0], int(row[1])
                        self.last_name_counts[name] += count
                        self.total_last_names += count
        
        except Exception as e:
            print(f"Error loading custom last name data: {e}")
    
    def _calculate_name_uniqueness(self, name, name_counts, total_names, print_components=False):
        """Internal method to calculate uniqueness score"""
        if not name or not isinstance(name, str):
            return 0
            
        name = name.strip().title()  # Normalize name format
        
        # Component 1: Frequency-based score
        frequency = name_counts.get(name.title(), 0) / total_names if total_names > 0 else 0
        if print_components:
            print(f"Frequency for {name}: {frequency}")
        if frequency == 0:
            # Name not in dataset, estimate rarity
            frequency_score = self.weights["unknown_name_base_score"]
            
            # Adjust based on letter n-grams
            bigrams = [name[i:i+2].lower() for i in range(len(name)-1)]
            all_names_text = ' '.join(name_counts.keys()).lower()
            bigram_rarity = sum(1 for bg in bigrams if ''.join(bg) not in all_names_text) / len(bigrams) if bigrams else 0
            frequency_score += bigram_rarity * self.weights["bigram_rarity_multiplier"]
        else:
            # Improved scaling for better contrast
            # Use exponential decay for more contrast between common and rare names
            w = self.weights
            if frequency < w["very_rare_threshold"]:  # Very rare names
                frequency_score = w["very_rare_base_score"] + (1 - frequency / w["very_rare_threshold"]) * w["very_rare_bonus_max"]
            elif frequency < w["uncommon_threshold"]:  # Uncommon names
                frequency_score = w["uncommon_base_score"] + (1 - frequency / w["uncommon_threshold"]) * w["uncommon_bonus_max"]
            elif frequency < w["moderate_threshold"]:   # Moderately common names
                frequency_score = w["moderate_base_score"] + (1 - frequency / w["moderate_threshold"]) * w["moderate_bonus_max"]
            elif frequency < w["common_threshold"]:   # Common names
                frequency_score = w["common_base_score"] + (1 - frequency / w["common_threshold"]) * w["common_bonus_max"]
            else:                   # Very common names
                frequency_score = max(w["very_common_max_score"] * (1 - frequency / w["very_common_scale_factor"]), 0)

        # Scale frequency score to the configured weight
        frequency_score = (frequency_score / 100) * self.weights["frequency_weight"]

        # Component 2: Structural uniqueness
        length_factor = min(len(name) / self.weights["max_name_length"], 1.0)
        unusual_chars = sum(1 for c in name if c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -\'')
        unusual_chars_factor = min(unusual_chars / self.weights["max_unusual_chars"], 1.0)
        
        structural_score = self.weights["structural_weight"] * (
            self.weights["length_factor_weight"] * length_factor + 
            self.weights["unusual_chars_weight"] * unusual_chars_factor
        )
        
        # Component 3: Letter distribution uniqueness
        letter_dist = Counter(name.lower())
        common_letters = sum(letter_dist[c] for c in 'etaoinshrdlu' if c in letter_dist) / len(name) if name else 0
        letter_uniqueness = self.weights["letter_dist_weight"] * (1 - common_letters)
        
        # Combine scores
        total_score = min(max(frequency_score + structural_score + letter_uniqueness, 0), 100)
        
        # Return both total score and component scores
        component_scores = {
            "frequency_score": round(frequency_score, 1),
            "structural_score": round(structural_score, 1),
            "letter_uniqueness": round(letter_uniqueness, 1),
            "total_score": round(total_score, 1)
        }
        
        return component_scores
    
    def calculate_first_name_uniqueness(self, name, print_components=False):
        """Calculate uniqueness score for a first name"""
        scores = self._calculate_name_uniqueness(name.title(), self.first_name_counts, self.total_first_names)
        if print_components:
            self.print_component_scores(name, scores)
        return scores["total_score"] if isinstance(scores, dict) else scores
    
    def calculate_last_name_uniqueness(self, name, print_components=False):
        """Calculate uniqueness score for a last name"""
        scores = self._calculate_name_uniqueness(name.title(), self.last_name_counts, self.total_last_names)
        if print_components:
            self.print_component_scores(name, scores)
        return scores["total_score"] if isinstance(scores, dict) else scores
    
    def print_component_scores(self, name, scores):
        """Print the component scores for a name"""
        if not isinstance(scores, dict):
            print(f"{name}: Total score = {scores}/100")
            return
            
        print(f"\nComponent scores for '{name}':")
        print(f"  Frequency-based score: {scores['frequency_score']}/{self.weights['frequency_weight']}")
        print(f"  Structural uniqueness: {scores['structural_score']}/{self.weights['structural_weight']}")
        print(f"  Letter distribution:   {scores['letter_uniqueness']}/{self.weights['letter_dist_weight']}")
        print(f"  Total score:           {scores['total_score']}/100")
    
    def calculate_full_name_uniqueness(self, first_name, last_name=None, print_components=False):
        """Calculate uniqueness score for a full name"""
        first_scores = self._calculate_name_uniqueness(first_name, self.first_name_counts, self.total_first_names, print_components)
        first_score = first_scores["total_score"] if isinstance(first_scores, dict) else first_scores
        
        if print_components:
            print(f"\nFull name analysis for '{first_name} {last_name or ''}':")
            if isinstance(first_scores, dict):
                print(f"First name '{first_name}':")
                print(f"  Frequency-based score: {first_scores['frequency_score']}/{self.weights['frequency_weight']}")
                print(f"  Structural uniqueness: {first_scores['structural_score']}/{self.weights['structural_weight']}")
                print(f"  Letter distribution:   {first_scores['letter_uniqueness']}/{self.weights['letter_dist_weight']}")
                print(f"  Total score:           {first_scores['total_score']}/100")
        
        if not last_name:
            return first_score
        
        last_scores = self._calculate_name_uniqueness(last_name, self.last_name_counts, self.total_last_names, print_components)
        last_score = last_scores["total_score"] if isinstance(last_scores, dict) else last_scores
        
        if print_components and isinstance(last_scores, dict):
            print(f"Last name '{last_name}':")
            print(f"  Frequency-based score: {last_scores['frequency_score']}/{self.weights['frequency_weight']}")
            print(f"  Structural uniqueness: {last_scores['structural_score']}/{self.weights['structural_weight']}")
            print(f"  Letter distribution:   {last_scores['letter_uniqueness']}/{self.weights['letter_dist_weight']}")
            print(f"  Total score:           {last_scores['total_score']}/100")
        
        # Improved combined scoring for better contrast
        # For extremely common first+last combinations, adjust score downward
        w = self.weights
        is_very_common_combo = False
        if first_score < w["common_combo_threshold"] and last_score < w["common_combo_threshold"]:
            is_very_common_combo = True
            # Exponentially reduce score for very common combinations like "John Smith"
            combined_score = (first_score * last_score) / w["common_combo_divisor"]
        else:
            # Normal weighting for most names
            # Rare first name + common last name is still quite unique
            combined_score = (first_score * w["first_name_weight"]) + (last_score * w["last_name_weight"])
        
        # Bonus for rare combinations
        bonus = 0
        if first_score > w["rare_combo_threshold"] and last_score > w["rare_combo_threshold"]:
            bonus = w["rare_combo_bonus"]
            combined_score += bonus

        rare_name_bonus = 1
        # Apply exponential bonus for uncommon names
        if first_score > 50:
            bonus_multiplier = math.exp((first_score - 50) / 50)
            if print_components:
                print(f"  Rare firstname multiplier: {bonus_multiplier}")
            rare_name_bonus *= max(1, min(bonus_multiplier, 2.0))  # Cap the multiplier at 2x
            
        if last_score > 50:
            bonus_multiplier = math.exp((last_score - 50) / 50)
            if print_components:
                print(f"  Rare lastname multiplier: {bonus_multiplier}")
            rare_name_bonus *= max(1, min(bonus_multiplier, 2.0))  # Cap the multiplier at 2x
            
        combined_score = min(round(combined_score, 1), 100)
        # Apply rare name bonus scaling to combined score
        if rare_name_bonus > 1:
            # Scale combined_score up based on rare_name_bonus (1-4)
            # When bonus is 4, score reaches 100
            # When bonus is 1, score stays the same
            combined_score = min(100, combined_score * (1 + (rare_name_bonus - 1) * (100 - combined_score) / 100))
            combined_score = round(combined_score, 1)
        
        if print_components:
            print(f"Combined score calculation:")
            if is_very_common_combo:
                print(f"  Very common combination: {first_score} × {last_score} / {w['common_combo_divisor']} = {round((first_score * last_score) / w['common_combo_divisor'], 1)}")
            elif first_score > 50 or last_score > 50:
                print(f"  Rare name multiplier: {rare_name_bonus}")
            else:
                print(f"  First name contribution: {first_score} × {w['first_name_weight']} = {round(first_score * w['first_name_weight'], 1)}")
                print(f"  Last name contribution:  {last_score} × {w['last_name_weight']} = {round(last_score * w['last_name_weight'], 1)}")
            if bonus > 0:
                print(f"  Rare combination bonus:  +{bonus}")
            print(f"  Final combined score:    {combined_score}/100")
        
        return combined_score
    
    def compare_names(self, names_list, name_type="first", print_components=False):
        """Compare uniqueness scores for a list of names"""
        results = []
        
        for name_entry in names_list:
            if isinstance(name_entry, tuple) and len(name_entry) >= 2:
                # Full name (first, last)
                first, last = name_entry
                score = self.calculate_full_name_uniqueness(first, last, print_components)
                results.append((f"{first} {last}", score))
            else:
                # Single name
                if name_type.lower() == "first":
                    score = self.calculate_first_name_uniqueness(name_entry, print_components)
                elif name_type.lower() == "last":
                    score = self.calculate_last_name_uniqueness(name_entry, print_components)
                else:
                    score = 0
                results.append((name_entry, score))
        
        # Sort by score descending
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def name_exists(self, name, name_type="first"):
        """
        Check if a name exists in our dataset.
        
        Args:
            name (str): The name to check
            name_type (str): Either "first" or "last" to specify which dataset to check
            
        Returns:
            bool: True if the name exists in our data, False otherwise
        """
        
        if name_type.lower() == "first":
            return name in self.first_name_counts
        elif name_type.lower() == "last":
            return name in self.last_name_counts
        else:
            raise ValueError("name_type must be either 'first' or 'last'")


# Example usage
if __name__ == "__main__":
    # Example paths
    ssa_data_dir = "./name_data"  # Directory with yobYYYY.txt files
    
    # Example of custom weights (optional)
    custom_weights = {
        "frequency_weight": 70,
        "structural_weight": 20,
        "letter_dist_weight": 10,
        "first_name_weight": 0.7,
        "last_name_weight": 0.3,
    }
    
    # Create scorer with default weights
    scorer = NameUniquenessScorer(ssa_data_dir)

    # print(scorer.first_name_counts)
    
    # Or create with custom weights
    # scorer = NameUniquenessScorer(ssa_data_dir, custom_weights=custom_weights)
    
    # Print current weight configuration
    print("=== Current Weight Configuration ===")
    for key, value in scorer.weights.items():
        print(f"{key}: {value}")
    print()
    
    # Test common vs unique names
    test_names = [
        ("James", "Williams"),   # Very common
        ("Emma", "Brown"),       # Very common
        ("Michael", "Jones"),    # Very common
        ("Elizabeth", "Garcia"), # Common
        ("Bertha", "Nguyen"),   # Uncommon first, common last
        ("Luna", "Zhang"),      # Modern unique first, common last
        ("Atlas", "Blackwood"), # Unique modern first, uncommon last
        ("River", "Phoenix"),   # Nature name + rare last name
        ("John", "Smith"),       # Very common
        ("Mary", "Johnson"),     # Very common
        ("Zephyr", "Moonbeam"),  # Unusual
        ("ouqhop", "qnod"),      # Made up/gibberish
        ("Xavier", "Rodriguez"), # Moderately common
        ("Allen", "Hentled"),
        ("Squi", "Borg"),
        ("Kaivon", "Larsen"),
        ("Abrielle", "Wolfeschlegelsteinhausenbergerdorff")  # Very rare combo
    ]

    test_names = [
        ("Douglas", "Douglas")
    ]
    
    print("\n=== Name Uniqueness Comparisons ===")
    for first, last in test_names:
        score = scorer.calculate_full_name_uniqueness(first, last, print_components=True)
        print(f"{first} {last}: {score}")
        print()