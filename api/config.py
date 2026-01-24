import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level up from api/)
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

# --- GCP Configuration ---
PROJECT_ID = os.getenv("PROJECT_ID")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
LOCATION = os.getenv("LOCATION", "us")

# Resolve credentials path relative to project root if not absolute.
# On Cloud Run, ADC is used automatically so credentials.json is not needed.
_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
if _creds_path:
    if not os.path.isabs(_creds_path):
        GOOGLE_APPLICATION_CREDENTIALS = str(_project_root / _creds_path)
    else:
        GOOGLE_APPLICATION_CREDENTIALS = _creds_path
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
else:
    GOOGLE_APPLICATION_CREDENTIALS = None

# --- App Configuration ---
PORT = int(os.getenv("PORT", "8080"))
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# --- Auth Configuration ---
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
