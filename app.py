# app.py (Final Version with Corrected Fetch Call)
# ---
# This script creates a web server that does two things:
# 1. On startup, pre-downloads the required court reporters database.
# 2. Serves the index.html file when a user visits the main page ('/').
# 3. Handles API requests to '/extract' to find legal citations.
# ---

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eyecite import get_citations
from reporters_db import cli # <-- CORRECTED IMPORT
import traceback

# Initialize the Flask application
app = Flask(__name__)

# --- Pre-load the reporters database on startup ---
print("Fetching reporters database...")
cli.fetch() # <-- CORRECTED FUNCTION CALL
print("Database fetch complete.")
# ----------------------------------------------------

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Route to serve the frontend
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/extract', methods=['POST'])
def extract_citations():
    """
    API endpoint to extract citations from a given block of text.
    Expects a JSON payload with a 'text' key and an optional 'format' key.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    text_to_scan = data.get('text')
    output_format = data.get('format', 'string')

    if not text_to_scan:
        return jsonify({"error": "No text provided"}), 400

    try:
        print("Received request. Starting citation extraction...")
        citations = get_citations(text_to_scan)
        print(f"Found {len(citations)} citations.")

        if output_format == 'json':
            print("Formatting as JSON.")
            result = [citation.json() for citation in citations]
        else:
            print("Formatting as string.")
            citation_list = [citation.matched_text for citation in citations]
            result = "; ".join(citation_list)
        
        print("Processing complete. Returning result.")
        return jsonify({"citations": result})

    except Exception as e:
        # --- MODIFIED: More detailed logging ---
        print("!!!!!!!!!! AN ERROR OCCURRED !!!!!!!!!!")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e}")
        print("Traceback:")
        traceback.print_exc() # This prints the full error stack trace
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return jsonify({"error": "Failed to process text"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


