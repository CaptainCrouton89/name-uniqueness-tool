import os
import sys

from flask import Flask, jsonify, request

# Add the parent directory to the path so we can import the NameUniquenessScorer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NameUniquenessScorer import NameUniquenessScorer

app = Flask(__name__)

# Initialize the scorer
scorer = NameUniquenessScorer(first_name_dir="./name_data")

@app.route('/api/score-name', methods=['POST'])
def score_name():
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

@app.route('/api/compare-names', methods=['POST'])
def compare_names():
    data = request.json
    names = data.get('names', [])
    
    if not names or not isinstance(names, list):
        return jsonify({"error": "A list of names is required"}), 400
    
    try:
        results = scorer.compare_names(names)
        return jsonify({
            "results": [
                {"name": name, "score": score} for name, score in results
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

# For local development
if __name__ == '__main__':
    app.run(debug=True) 