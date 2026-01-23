"""Entry point for running the Flask development server."""
from api import create_app
from api.config import PORT, DEBUG, PROJECT_ID, DATA_STORE_ID

app = create_app()

if __name__ == '__main__':
    print(f"Starting server... PROJECT_ID={PROJECT_ID}, DATA_STORE_ID={DATA_STORE_ID}")
    app.run(port=PORT, debug=DEBUG)
