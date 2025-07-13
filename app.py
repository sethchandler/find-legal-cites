# app.py (Final Version with Robust Extraction Logic)
# ---
# This script creates a web server that does two things:
# 1. On startup, pre-downloads the required court reporters database.
# 2. Serves the index.html file when a user visits the main page ('/').
# 3. Handles API requests to '/extract' to find legal citations using
#    a robust method that handles library edge cases.
# ---

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eyecite import get_citations
from reporters_db import cli
import traceback

# Initialize the Flask application
app = Flask(__name__)

# --- Pre-load the reporters database on startup ---
print("Fetching reporters database...")
cli.fetch()
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
        
        # --- NEW ROBUST LOGIC ---
        # Use with_spans=True to get character offsets. This is more reliable
        # than relying on the citation object's internal state.
        citations_with_spans = get_citations(text_to_scan, with_spans=True)
        print(f"Found {len(citations_with_spans)} potential citations.")

        if output_format == 'json':
            print("Formatting as JSON.")
            # The .json() method is generally safe. We extract the citation
            # object from the tuple before calling it.
            result = [citation.json() for citation, span in citations_with_spans]
        else:
            print("Formatting as string.")
            # Use the spans to slice the original text. This avoids errors
            # from malformed .matched_text attributes.
            citation_list = [text_to_scan[span[0]:span[1]] for citation, span in citations_with_spans]
            result = "; ".join(citation_list)
        
        print("Processing complete. Returning result.")
        return jsonify({"citations": result})

    except Exception as e:
        print("!!!!!!!!!! AN ERROR OCCURRED !!!!!!!!!!")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e}")
        print("Traceback:")
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return jsonify({"error": "Failed to process text"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)




