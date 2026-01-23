import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from dotenv import load_dotenv

load_dotenv()

# Config
PROJECT_ID = os.getenv("PROJECT_ID")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
LOCATION = os.getenv("LOCATION", "us")
BRANCH_ID = "default_branch" # usually 0 or default_branch

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
            # print(f"Data: {doc.struct_data}")
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
