#!/bin/bash
set -e

# --- Ensure gcloud is in PATH (especially for first-time Homebrew installs) ---
if ! command -v gcloud &> /dev/null; then
  if [ -d "/opt/homebrew/share/google-cloud-sdk/bin" ]; then
    export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
  elif [ -d "/usr/local/share/google-cloud-sdk/bin" ]; then
    export PATH="/usr/local/share/google-cloud-sdk/bin:$PATH"
  fi
fi

if ! command -v gcloud &> /dev/null; then
  echo "ERROR: gcloud command not found. Please ensure Google Cloud SDK is installed and in your PATH."
  exit 1
fi

# --- Configuration ---
PROJECT_ID="ai-poc-project-483817"
REGION="us-central1"
SERVICE_NAME="buddy-fetch"
REPO_NAME="buddy-fetch"
IMAGE="us-central1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/app"

# --- Check for required password ---
if [ -z "$APP_PASSWORD" ]; then
  echo "ERROR: Set APP_PASSWORD environment variable before deploying."
  echo "  export APP_PASSWORD='eron_sucks_1234'"
  exit 1
fi

echo "==> Building and pushing container image..."
gcloud builds submit --tag "${IMAGE}" --project "${PROJECT_ID}"

echo "==> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=${PROJECT_ID},DATA_STORE_ID=eron-data-01_1769215596289,LOCATION=global,APP_PASSWORD=${APP_PASSWORD}" \
  --max-instances 3 \
  --memory 512Mi \
  --timeout 120

echo ""
echo "==> Deployed! Your app URL:"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --project "${PROJECT_ID}" --format="value(status.url)"
