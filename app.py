# app.py (Final Fixed Version with Method Calls and Enhanced Logging)
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
        print("Invalid request: Not JSON.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    text_to_scan = data.get('text')
    output_format = data.get('format', 'string')

    if not text_to_scan:
        print("Invalid request: No text provided.")
        return jsonify({"error": "No text provided"}), 400

    try:
        print("Received request. Text length: {}".format(len(text_to_scan)))
        print("Output format requested: {}".format(output_format))
        print("Starting citation extraction...")
        
        # --- ROBUST LOGIC ---
        # Use with_spans=True to get character offsets. This is more reliable
        # than relying on the citation object's internal state.
        citations_with_spans = get_citations(text_to_scan, with_spans=True)
        print(f"Found {len(citations_with_spans)} potential citations."")
        print("Citations with spans: {}".format([(str(citation), span) for citation, span in citations_with_spans]))
        
        if output_format == 'json':
            print("Formatting as JSON.")
            # Manual serialization since no .json() method exists. Include called .matched_text().
            result = []
            for citation, span in citations_with_spans:
                cite_dict = {
                    'type': type(citation).__name__,
                    'matched_text': citation.matched_text(),  # Call the method
                    'groups': citation.groups,
                    'metadata': vars(citation.metadata) if citation.metadata else None,
                    'span': span
                }
                result.append(cite_dict)
            print("JSON results sample (first item): {}".format(result[0] if result else "None"))
        else:
            print("Formatting as string.")
            # Call .matched_text() to get the strings reliably
            citation_list = [citation.matched_text() for citation, span in citations_with_spans]
            print("Extracted citation strings: {}".format(citation_list))
            result = "; ".join(citation_list)
        
        print("Processing complete. Returning result.")
        return jsonify({"citations": result})

    except Exception as e:
        print("!!!!!!!!!! AN ERROR OCCURRED !!!!!!!!!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return jsonify({"error": "Failed to process text"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)




