import hashlib
import hmac
from flask import request, jsonify
from api.config import APP_PASSWORD
from api.services.search import search_documents


def _generate_token(password):
    """Generate a stateless token from the password."""
    return hmac.new(password.encode(), b"buddy-fetch-auth", hashlib.sha256).hexdigest()


def _check_auth():
    """Validate the Authorization header token. Returns error response or None."""
    if not APP_PASSWORD:
        return None  # No password configured, allow all
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    token = auth[len("Bearer "):]
    expected = _generate_token(APP_PASSWORD)
    if not hmac.compare_digest(token, expected):
        return jsonify({"error": "Unauthorized"}), 401
    return None


def register_routes(app):
    """Register all API routes on the Flask app."""

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"})

    @app.route('/verify-password', methods=['POST'])
    def verify_password():
        if not APP_PASSWORD:
            return jsonify({"token": "no-auth-required"})
        data = request.json or {}
        password = data.get('password', '')
        if not hmac.compare_digest(password, APP_PASSWORD):
            return jsonify({"error": "Invalid password"}), 401
        token = _generate_token(APP_PASSWORD)
        return jsonify({"token": token})

    @app.route('/search', methods=['POST'])
    def search():
        auth_error = _check_auth()
        if auth_error:
            return auth_error

        data = request.json
        query = data.get('query', '')
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)

        # Build filter string from individual filter fields
        filters = data.get('filters', {})
        filter_parts = []

        # Supported filterable fields: sender, subject, to
        # All use ANY() syntax for Discovery Engine
        for field in ['sender', 'subject', 'to']:
            value = filters.get(field)
            if value:
                escaped_value = value.replace('"', '\\"')
                filter_parts.append(f'{field}: ANY("{escaped_value}")')

        filter_str = ' AND '.join(filter_parts) if filter_parts else None

        if not query:
            return jsonify({"error": "No query provided"}), 400

        offset = (page - 1) * page_size

        try:
            result = search_documents(query, offset=offset, page_size=page_size, filter_str=filter_str)
            return jsonify({
                "results": result["results"],
                "total_size": result["total_size"],
                "page": page,
                "page_size": page_size,
                "summary": result["summary"],
                "summary_references": result["summary_references"],
                "applied_filter": filter_str,
            })
        except Exception as e:
            print(f"Error during search: {e}")
            return jsonify({"error": str(e)}), 500
