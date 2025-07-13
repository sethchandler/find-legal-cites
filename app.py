# app.py (Updated Version with Case Name Inclusion Option)
# ---
# This script creates a web server that:
# 1. Serves the index.html file when a user visits the main page ('/').
# 2. Handles API requests to '/extract' to find legal citations from text.
#    - Uses eyecite's get_citations without spans for simplicity.
#    - For string format: Optionally includes reconstructed case names.
#    - Formats as string (joined with/without case names) or JSON (manual dicts).
#    - Includes diagnostic logging.
# ---

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from eyecite import get_citations
import traceback

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Route to serve the frontend
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

def format_with_case_name(citation):
    """
    Formats a citation with reconstructed case name if available (approximating Bluebook style).
    - For FullCaseCitation: Plaintiff v. Defendant, Volume Reporter Page (Year) if available.
    - Fallback for others: corrected_citation() or matched_text().
    """
    if 'FullCaseCitation' in str(type(citation)):
        meta = citation.metadata
        plaintiff = getattr(meta, 'plaintiff', '')
        defendant = getattr(meta, 'defendant', '')
        year = getattr(meta, 'year', '')
        parties = f"{plaintiff} v. {defendant}".strip()
        core_cite = citation.corrected_citation()
        year_str = f" ({year})" if year else ''
        return f"{parties}, {core_cite}{year_str}".strip(', ')
    else:
        # Fallback for short cites, statutes, etc.
        return citation.corrected_citation() or citation.matched_text()

@app.route('/extract', methods=['POST'])
def extract_citations():
    """
    API endpoint to extract citations from a given block of text.
    Expects a JSON payload with a 'text' key, optional 'format' key ('string' or 'json'),
    and optional 'include_case_names' boolean (for string format only).
    """
    if not request.is_json:
        print("Invalid request: Not JSON.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    text_to_scan = data.get('text')
    output_format = data.get('format', 'string')
    include_case_names = data.get('include_case_names', False)

    if not text_to_scan:
        print("Invalid request: No text provided.")
        return jsonify({"error": "No text provided"}), 400

    try:
        print("Received request. Text length: {}".format(len(text_to_scan)))
        print("Output format requested: {}".format(output_format))
        print("Include case names: {}".format(include_case_names))
        print("Starting citation extraction...")
        
        # Extract citations simply (no with_spans=True, as not needed for basic cases)
        citations = get_citations(text_to_scan)
        print(f"Found {len(citations)} potential citations.")
        print("Citations: {}".format([str(citation) for citation in citations]))
        
        if output_format == 'json':
            print("Formatting as JSON.")
            # Manual serialization: Use method calls like matched_text() and corrected_citation()
            result = []
            for citation in citations:
                cite_dict = {
                    'type': type(citation).__name__,
                    'matched_text': citation.matched_text(),
                    'corrected_citation': citation.corrected_citation(),
                    'groups': citation.groups,
                    'metadata': vars(citation.metadata) if citation.metadata else None,
                    'span': citation.span()  # Include span via method if available
                }
                result.append(cite_dict)
            print("JSON results sample (first item): {}".format(result[0] if result else "None"))
        else:
            print("Formatting as string.")
            if include_case_names:
                citation_list = [format_with_case_name(citation) for citation in citations]
            else:
                citation_list = [citation.matched_text() for citation in citations]
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



