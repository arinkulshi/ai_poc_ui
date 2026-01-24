import os
from flask import Flask, send_from_directory
from flask_cors import CORS

_ui_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ui', 'dist')


def create_app():
    """Application factory for the Flask app."""
    app = Flask(__name__, static_folder=_ui_dist, static_url_path='')
    CORS(app)

    from api.routes import register_routes
    register_routes(app)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve the React SPA. API routes take priority via register_routes."""
        file_path = os.path.join(_ui_dist, path)
        if path and os.path.isfile(file_path):
            return send_from_directory(_ui_dist, path)
        return send_from_directory(_ui_dist, 'index.html')

    return app
