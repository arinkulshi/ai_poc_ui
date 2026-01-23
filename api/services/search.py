from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from api.config import PROJECT_ID, LOCATION, DATA_STORE_ID


def search_documents(query: str) -> list:
    """Performs a search against the Vertex AI Search Data Store."""
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )

    client = discoveryengine.SearchServiceClient(client_options=client_options)

    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        serving_config="default_search",
    )

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
        doc_data = result.document.struct_data

        title = data.get("title") or doc_data.get("subject") or "No Title"

        snippet = ""
        if doc_data.get("abstract"):
            snippet = str(doc_data.get("abstract"))
        elif doc_data.get("text_content"):
            snippet = str(doc_data.get("text_content"))[:300] + "..."

        if data.get("extractive_segments"):
            seg = data["extractive_segments"][0].get("content", "")
            if seg:
                snippet = seg

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
            "agency": doc_data.get("agency", "Unknown"),
        })

    return results
