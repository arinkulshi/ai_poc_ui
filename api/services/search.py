from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from api.config import PROJECT_ID, LOCATION, ENGINE_ID


from typing import Optional

def search_documents(query: str, offset: int = 0, page_size: int = 10, filter_str: Optional[str] = None) -> dict:
    """Performs a search against the Vertex AI Search engine (unstructured data)."""
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )

    client = discoveryengine.SearchServiceClient(client_options=client_options)

    # Engine-based serving config path
    serving_config = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}"
        f"/collections/default_collection/engines/{ENGINE_ID}"
        f"/servingConfigs/default_search"
    )

    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True,
        ),
        extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_segment_count=1,
        ),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=False,
            ignore_non_summary_seeking_query=False,
        ),
    )

    request_obj = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
        offset=offset,
        filter=filter_str,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request_obj)
    total_size = response.total_size

    results = []
    for result in response.results:
        data = result.document.derived_struct_data
        doc_data = result.document.struct_data

        title = doc_data.get("subject") or data.get("title") or "No Subject"

        # Snippets from unstructured data have <b> highlighted terms
        snippet = ""
        if data.get("snippets"):
            for s in data["snippets"]:
                snippet_text = s.get("snippet", "")
                if snippet_text and "no snippet" not in snippet_text.lower():
                    snippet = snippet_text
                    break

        # Extractive segments provide longer content for the drawer view
        body = ""
        if data.get("extractive_segments"):
            seg = data["extractive_segments"][0].get("content", "")
            if seg:
                body = seg

        if not snippet and body:
            snippet = body[:250] + ("..." if len(body) > 250 else "")

        author = (doc_data.get("sender_name")
                  or doc_data.get("sender")
                  or "Unknown")

        results.append({
            "id": result.document.id,
            "title": title,
            "snippet": snippet,
            "date": doc_data.get("date", ""),
            "body": body or snippet,
            "author": author,
            "to": doc_data.get("to", "Unknown"),
            "folder": doc_data.get("folder", ""),
        })

    # Extract AI summary with citations
    summary_text = ""
    summary_references = []
    if response.summary and response.summary.summary_text:
        summary_text = response.summary.summary_text
        # Map citation numbers [1], [2], etc. to result documents
        if response.summary.summary_with_metadata:
            for ref in response.summary.summary_with_metadata.references:
                summary_references.append({
                    "title": ref.title or "",
                    "document": ref.document,
                })

    return {
        "results": results,
        "total_size": total_size,
        "summary": summary_text,
        "summary_references": summary_references,
    }
