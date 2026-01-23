"""List documents in the configured data store."""
import sys
from pathlib import Path

# Add project root to path so we can import the api package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from api.config import PROJECT_ID, DATA_STORE_ID, LOCATION

BRANCH_ID = "default_branch"


def list_documents():
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}/branches/{BRANCH_ID}"

    print(f"Listing Documents in: {parent}")
    try:
        request = discoveryengine.ListDocumentsRequest(parent=parent, page_size=10)
        response = client.list_documents(request=request)

        count = 0
        for doc in response:
            count += 1
            print(f"Doc ID: {doc.id}")
            if count >= 5:
                break

        if count == 0:
            print("No documents found in the index.")
        else:
            print(f"Found at least {count} documents.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    list_documents()
