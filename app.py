import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for the UI

# --- Configuration ---
PROJECT_ID = os.getenv("PROJECT_ID")
DATA_STORE_ID = os.getenv("DATA_STORE_ID")
LOCATION = os.getenv("LOCATION", "us")

def search_sample(project_id: str, location: str, data_store_id: str, query: str):
    """
    Performs a search against the Vertex AI Search Data Store.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    
    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    
    # The full resource name of the search engine serving config
    # e.g. projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/servingConfigs/default_search
    serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        serving_config="default_search",
    )
    
    # Optional: content_search_spec for snippet extraction
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
        ),
    )

    request_obj = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=10,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request_obj)
    
    results = []
    for result in response.results:
        data = result.document.derived_struct_data
        
        # Unstructured data often puts content in 'snippets' or 'extractive_segments'
        # But since we uploaded JSONL, the fields might be accessible directly depending on schema settings.
        # Fallback to snippet if specific fields aren't found.
        
        # Try to grab fields we know exist in our dummy data
        # Note: In "Unstructured" mode with JSONL, fields might be flattened or inside 'structData'
        # We will inspect the result structure to be safe.
        
        doc_data = result.document.struct_data 
        
        # Handle title
        title = data.get("title") or doc_data.get("subject") or "No Title"
        
        # DEBUG: Print structure to see what we are getting
        # print(f"DEBUG DATA: {data}")
        # print(f"DEBUG DOC_DATA: {doc_data}")
        
        # Handle snippet
        snippet = ""
        
        # 0. Force check the known text field first for this POC
        # Use our pre-computed 'abstract' if available, otherwise 'text_content'
        if doc_data.get("abstract"):
             snippet = str(doc_data.get("abstract"))
        elif doc_data.get("text_content"):
             # Truncate to reasonable length for a snippet
             snippet = str(doc_data.get("text_content"))[:300] + "..."

        # 1. Fallback to Extractive Segments if available and better
        if data.get("extractive_segments"):
            # Only override if we specifically want the "AI found this" segment
            # For a POC, sometimes raw text is safer if extraction is cold.
            seg = data["extractive_segments"][0].get("content", "")
            if seg: snippet = seg

        results.append({
            "id": result.document.id,
            "title": title,
            "snippet": snippet,
            "url": doc_data.get("url", "#"),
            "date": doc_data.get("date", ""),
            "score": result.document.id,
            "body": doc_data.get("text_content", "No content available."),
            "author": doc_data.get("author", "Unknown"),
            "to": doc_data.get("to", "Unknown"),
            "agency": doc_data.get("agency", "Unknown")
        })
        
    return results

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
        results = search_sample(PROJECT_ID, LOCATION, DATA_STORE_ID, query)
        return jsonify({"results": results})
    except Exception as e:
        print(f"Error during search: {e}")
        # Return error details to help debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Starting server... PROJECT_ID={PROJECT_ID}, DATA_STORE_ID={DATA_STORE_ID}")
    app.run(port=8080, debug=True)
