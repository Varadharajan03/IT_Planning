import time
from ddgs  import DDGS
def search_duckduckgo(query, max_results=5):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            snippets = []
            for i, result in enumerate(results, 1):
                print(f"Result {i}:")
                print(f"Title: {result['title']}")
                print(f"URL: {result['href']}")
                print(f"Snippet: {result['body']}")
                print("-" * 50)
                snippets.append(result['body'])
            return snippets if snippets else ["No relevant results found."]
    except Exception as e:
        print(f"Search failed: {str(e)}")
        time.sleep(1)  # Wait before retrying
        return [f"Search failed: {str(e)}"]