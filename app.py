# app.py (Updated)
# ---
# This script creates a simple web server using the Flask framework.
# It exposes a single API endpoint '/extract' that accepts text
# and an optional 'format' parameter ('string' or 'json').
#
# It uses the 'eyecite' library to find legal citations and returns
# them either as a semi-colon delimited string or a JSON array
# of structured citation objects.
# ---

from flask import Flask, request, jsonify
from flask_cors import CORS
from eyecite import get_citations

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

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
    # Get the desired format, defaulting to 'string' if not provided
    output_format = data.get('format', 'string')

    if not text_to_scan:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Use eyecite's get_citations function to find all citations
        citations = get_citations(text_to_scan)

        # Check the desired output format
        if output_format == 'json':
            # Use the built-in .json() method for each citation object
            # to get a list of structured dictionary objects.
            result = [citation.json() for citation in citations]
        else:
            # Default to the original behavior: a simple, delimited string.
            citation_list = [citation.matched_text for citation in citations]
            result = "; ".join(citation_list)

        # Return the result in a JSON object. The key is always "citations",
        # but the value can be either a string or a list of objects.
        return jsonify({"citations": result})

    except Exception as e:
        # Handle any potential errors during the citation extraction process
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to process text"}), 500

# This block allows the script to be run directly.
if __name__ == '__main__':
    app.run(debug=True, port=5000)
