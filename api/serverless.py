import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler

# Add the parent directory to the path so we can import the NameUniquenessScorer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from NameUniquenessScorer import NameUniquenessScorer

# Initialize the scorer with the correct path to name_data
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name_data_path = os.path.join(parent_dir, "name_data")
scorer = NameUniquenessScorer(first_name_dir=name_data_path)

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            if self.path == "/api/score-name":
                result = self._handle_score_name(data)
                status_code = 200
            elif self.path == "/api/compare-names":
                result = self._handle_compare_names(data)
                status_code = 200
            else:
                result = {"error": "Not found"}
                status_code = 404
            
            self.send_response(status_code)
            self._set_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self._set_cors_headers()
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_message = {"error": str(e), "traceback": traceback.format_exc()}
            self.wfile.write(json.dumps(error_message).encode())
    
    def _handle_score_name(self, data):
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')
        
        if not first_name and not last_name:
            return {"error": "At least one name is required"}
        
        if first_name and last_name:
            score = scorer.calculate_full_name_uniqueness(first_name, last_name)
            return {
                "firstName": first_name,
                "lastName": last_name,
                "fullName": f"{first_name} {last_name}",
                "score": score,
                "type": "full"
            }
        elif first_name:
            score = scorer.calculate_first_name_uniqueness(first_name)
            return {
                "firstName": first_name,
                "score": score,
                "type": "first"
            }
        else:
            score = scorer.calculate_last_name_uniqueness(last_name)
            return {
                "lastName": last_name,
                "score": score,
                "type": "last"
            }
    
    def _handle_compare_names(self, data):
        names = data.get('names', [])
        
        if not names or not isinstance(names, list):
            return {"error": "A list of names is required"}
        
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
        return {
            "results": [
                {"name": name, "score": score} for name, score in results
            ]
        } 