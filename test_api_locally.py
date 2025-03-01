#!/usr/bin/env python3
"""
Test script for the Name Uniqueness API
Run this script to test the API locally before deploying to Vercel
"""

import http.server
import os
import socketserver
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the handler from the API
from api.index import handler

PORT = 5001

class TestServer(http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)

def run_test_server():
    with TestServer(("", PORT), handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Test the API with:")
        print(f"  - GET http://localhost:{PORT}/api")
        print(f"  - POST http://localhost:{PORT}/api/score-name")
        print(f"  - POST http://localhost:{PORT}/api/compare-names")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")

if __name__ == "__main__":
    run_test_server() 