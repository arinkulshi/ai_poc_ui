from flask import request, jsonify
from api.services.search import search_documents


def register_routes(app):
    """Register all API routes on the Flask app."""

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"})

    @app.route('/search', methods=['POST'])
    def search():
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({"error": "No query provided"}), 400

        try:
            results = search_documents(query)
            return jsonify({"results": results})
        except Exception as e:
            print(f"Error during search: {e}")
            return jsonify({"error": str(e)}), 500
