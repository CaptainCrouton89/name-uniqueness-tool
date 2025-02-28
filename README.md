# Name Uniqueness Score Tool

A Python tool for calculating the uniqueness of names based on frequency, structural characteristics, and letter distribution.

## Features

- Calculate uniqueness scores for first names, last names, or full names
- Compare multiple names and rank them by uniqueness
- Configurable scoring weights for different uniqueness factors
- Uses real-world name frequency data from US Census and SSA

## Usage

```python
from NameUniquenessScorer import NameUniquenessScorer

# Initialize with default weights
scorer = NameUniquenessScorer(first_name_dir="./name_data")

# Calculate uniqueness for a single name
score = scorer.calculate_first_name_uniqueness("Luna")
print(f"Luna: {score}/100")

# Calculate uniqueness for a full name
score = scorer.calculate_full_name_uniqueness("River", "Phoenix")
print(f"River Phoenix: {score}/100")

# Compare multiple names
names = [
    ("James", "Williams"),
    ("Luna", "Zhang"),
    ("Zephyr", "Moonbeam")
]
results = scorer.compare_names(names)
for name, score in results:
    print(f"{name}: {score}/100")
```

## Scoring Factors

The uniqueness score (0-100) is based on:

1. **Frequency** (80%): How common the name is in population data
2. **Structural uniqueness** (10%): Length and unusual characters
3. **Letter distribution** (10%): Rarity of letter combinations

## Requirements

- Python 3.6+
- Name frequency data files (not included)
