import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the parent directory to the path so we can import the NameUniquenessScorer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NameUniquenessScorer import NameUniquenessScorer

app = Flask(__name__)
CORS(app)

# Initialize the scorer with the correct path to name_data
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name_data_path = os.path.join(parent_dir, "name_data")
scorer = NameUniquenessScorer(first_name_dir=name_data_path)

def score_name_handler(request):
    data = request.json
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')
    
    if not first_name and not last_name:
        return jsonify({"error": "At least one name is required"}), 400
    
    try:
        if first_name and last_name:
            score = scorer.calculate_full_name_uniqueness(first_name, last_name)
            result = {
                "firstName": first_name,
                "lastName": last_name,
                "fullName": f"{first_name} {last_name}",
                "score": score,
                "type": "full"
            }
        elif first_name:
            score = scorer.calculate_first_name_uniqueness(first_name)
            result = {
                "firstName": first_name,
                "score": score,
                "type": "first"
            }
        else:
            score = scorer.calculate_last_name_uniqueness(last_name)
            result = {
                "lastName": last_name,
                "score": score,
                "type": "last"
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def compare_names_handler(request):
    data = request.json
    names = data.get('names', [])
    
    if not names or not isinstance(names, list):
        return jsonify({"error": "A list of names is required"}), 400
    
    try:
        # Ensure all names are strings, not nested lists
        processed_names = []
        for name_entry in names:
            if isinstance(name_entry, list):
                # If it's a list with at least 2 elements, treat as [first_name, last_name]
                if len(name_entry) >= 2:
                    processed_names.append((name_entry[0], name_entry[1]))
                elif len(name_entry) == 1:
                    processed_names.append(name_entry[0])
                # Skip empty lists
            elif isinstance(name_entry, dict):
                # If it's a dict, look for firstName and lastName keys
                first = name_entry.get('firstName', '')
                last = name_entry.get('lastName', '')
                if first and last:
                    processed_names.append((first, last))
                elif first:
                    processed_names.append(first)
                elif last:
                    processed_names.append(last)
            else:
                # Assume it's a string
                processed_names.append(name_entry)
        
        results = scorer.compare_names(processed_names)
        return jsonify({
            "results": [
                {"name": name, "score": score} for name, score in results
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def health_check_handler(request):
    return jsonify({"status": "ok"})

# Vercel serverless function handler
def handler(request):
    path = request.path
    
    if path == "/api/score-name":
        if request.method == "POST":
            return score_name_handler(request)
    elif path == "/api/compare-names":
        if request.method == "POST":
            return compare_names_handler(request)
    elif path == "/api/health":
        if request.method == "GET":
            return health_check_handler(request)
    
    return jsonify({"error": "Not found"}), 404 