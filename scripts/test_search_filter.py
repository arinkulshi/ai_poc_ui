import sys
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.services.search import search_documents

def test_search(query, filter_str=None):
    print(f"Searching for: '{query}' with filter: '{filter_str}'")
    try:
        results = search_documents(query, filter_str=filter_str)
            
        print(f"Found {results['total_size']} results")
        for res in results['results'][:3]:
            # Print agency to see if it matches filter
            print(f" - {res['title']} (Agency: {res.get('folder', '')} / Author: {res.get('author', '')})")
            # Note: The search_documents response maps fields. 'agency' might not be in the results dict directly if not mapped.
            # Let's check api/services/search.py again. 
            # It maps title, snippet, date, body, author, to, folder.
            # Does it map agency? No.
            # I should probably inspect the raw output if I want to debug, but existing code doesn't return agency.
            # Wait, api/services/search.py does NOT put 'agency' in the result dict.
            # However, I can still filter by it.
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("--- Test 1: No Filter ---")
    test_search("white house")

    # Success Case: Date Filter
    print("\n--- Test 2: Filter date >= '2000-01-01' (Expect results) ---")
    test_search("white house", filter_str='date >= "2000-01-01"')

    # Success Case: Date Filter
    print("\n--- Test 2: Filter date >= '2000-01-01' ---")
    test_search("white house", filter_str='date >= "2000-01-01"')

    # Test uri (often indexed by default, check if we can filter by it)
    # The error message for agency was "Unsupported field".
    # If uri is supported, it should work.
    # Note: wildcard filtering on URI is not always supported, but equality or check might be.
    # Let's try to find documents containing "gmail" in uri if that's even possible, 
    # OR just check if it accepts the field name even if we match nothing.
    print("\n--- Test 3: Filter uri : 'gs://' ---")
    test_search("white house", filter_str='uri: "gs://"')

    # Maybe creating_time?
    # Discovery Engine fields are specific. 'createTime'
    # print("\n--- Test 4: Filter createTime >= 0 ---")
    # test_search("white house", filter_str='createTime >= 0')






