"""List all data stores in the configured GCP project."""
import sys
from pathlib import Path

# Add project root to path so we can import the api package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from api.config import PROJECT_ID, LOCATION


def list_data_stores():
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"

    print(f"Listing Data Stores in: {parent}")
    try:
        response = client.list_data_stores(parent=parent)
        found = False
        for ds in response:
            found = True
            print(f"Name: {ds.display_name}")
            print(f"ID: {ds.name.split('/')[-1]}")
            print(f"Full Name: {ds.name}")
            print("-" * 20)

        if not found:
            print("No data stores found. Check Project ID and Location.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    list_data_stores()
