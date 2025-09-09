import requests

def duckduckgo_search(query, max_results=3):
    url = "https://api.duckduckgo.com/"
    params = {
        'q': query,
        'format': 'json',
        'no_redirect': 1,
        'no_html': 1,
        'skip_disambig': 1
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = []

        if data.get('AbstractText'):
            results.append(data['AbstractText'])

        for topic in data.get('RelatedTopics', [])[:max_results]:
            if 'Text' in topic:
                results.append(topic['Text'])

        return results
    except Exception as e:
        return [f"Search failed: {str(e)}"]
