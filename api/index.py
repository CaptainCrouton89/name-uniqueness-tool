import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('name_uniqueness_api')

# Add the parent directory to sys.path to import the name_uniqueness_scorer
sys.path.append(str(Path(__file__).resolve().parent.parent))

from name_uniqueness_scorer import NameUniquenessScorer

# Initialize the scorer with the name data
name_data_dir = str(Path(__file__).resolve().parent.parent / "name_data")
last_name_source = str(Path(__file__).resolve().parent.parent / "name_data" / "last_names.csv")

try:
    scorer = NameUniquenessScorer(
        first_name_dir=name_data_dir,
        last_name_source=last_name_source
    )
    logger.info("Name Uniqueness Scorer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Name Uniqueness Scorer: {str(e)}")
    raise

def cors_headers():
    """Return CORS headers for cross-origin requests"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override default log_message to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))
        
    def do_OPTIONS(self):
        """Handle preflight requests for CORS"""
        self.send_response(200)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Name Uniqueness API is running"
        }
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            logger.info(f"POST request to {self.path} with data: {data}")
            
            # Route to the appropriate handler based on the path
            if self.path == '/api/score-name':
                response = self.handle_score_name(data)
                self.send_response(200)
            elif self.path == '/api/compare-names':
                response = self.handle_compare_names(data)
                self.send_response(200)
            else:
                logger.warning(f"Invalid endpoint requested: {self.path}")
                response = {"error": "Invalid endpoint"}
                self.send_response(404)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {str(e)}")
            response = {"error": "Invalid JSON"}
            self.send_response(400)
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            response = {"error": str(e)}
            self.send_response(500)
        
        self.send_header('Content-type', 'application/json')
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_score_name(self, data):
        """Handle name scoring requests"""
        first_name = data.get('firstName', '').strip()
        last_name = data.get('lastName', '').strip()
        
        if not first_name and not last_name:
            logger.warning("Score name request with no names provided")
            return {"error": "Please provide at least one name"}
        
        try:
            if first_name and last_name:
                # Score full name
                logger.info(f"Scoring full name: {first_name} {last_name}")
                score = scorer.calculate_full_name_uniqueness(first_name, last_name)
                return {
                    "score": round(score),
                    "type": "full",
                    "fullName": f"{first_name} {last_name}",
                    "firstName": first_name,
                    "lastName": last_name
                }
            elif first_name:
                # Score first name only
                logger.info(f"Scoring first name: {first_name}")
                score = scorer.calculate_first_name_uniqueness(first_name)
                return {
                    "score": round(score),
                    "type": "first",
                    "firstName": first_name
                }
            else:
                # Score last name only
                logger.info(f"Scoring last name: {last_name}")
                score = scorer.calculate_last_name_uniqueness(last_name)
                return {
                    "score": round(score),
                    "type": "last",
                    "lastName": last_name
                }
        except Exception as e:
            logger.error(f"Error scoring name: {str(e)}", exc_info=True)
            raise

    def handle_compare_names(self, data):
        """Handle name comparison requests"""
        names_list = data.get('names', [])
        
        if not names_list:
            logger.warning("Compare names request with no names provided")
            return {"error": "Please provide names to compare"}
        
        logger.info(f"Comparing {len(names_list)} names")
        results = []
        
        try:
            for i, name_pair in enumerate(names_list):
                if len(name_pair) >= 2:
                    first_name, last_name = name_pair[0], name_pair[1]
                    
                    if first_name and last_name:
                        # Full name
                        logger.debug(f"Scoring full name #{i+1}: {first_name} {last_name}")
                        score = scorer.calculate_full_name_uniqueness(first_name, last_name)
                        results.append({
                            "name": f"{first_name} {last_name}",
                            "score": round(score)
                        })
                    elif first_name:
                        # First name only
                        logger.debug(f"Scoring first name #{i+1}: {first_name}")
                        score = scorer.calculate_first_name_uniqueness(first_name)
                        results.append({
                            "name": first_name,
                            "score": round(score)
                        })
                    elif last_name:
                        # Last name only
                        logger.debug(f"Scoring last name #{i+1}: {last_name}")
                        score = scorer.calculate_last_name_uniqueness(last_name)
                        results.append({
                            "name": last_name,
                            "score": round(score)
                        })
                elif len(name_pair) == 1 and name_pair[0]:
                    # Single name (treat as first name)
                    logger.debug(f"Scoring single name #{i+1}: {name_pair[0]}")
                    score = scorer.calculate_first_name_uniqueness(name_pair[0])
                    results.append({
                        "name": name_pair[0],
                        "score": round(score)
                    })
            
            return {"results": results}
        except Exception as e:
            logger.error(f"Error comparing names: {str(e)}", exc_info=True)
            raise 