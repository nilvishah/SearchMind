# tools/web_search.py
from tavily import TavilyClient
from config import TAVILY_API_KEY

client = TavilyClient(api_key=TAVILY_API_KEY)

def web_search(query: str, max_results: int = 3) -> list[dict]:  # ← 5 to 3
    """
    Search the live web for a query.
    Returns a list of results with title, url, and content snippet.
    """
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic"  # ← advanced to basic (shorter snippets)
    )

    results = []
    for r in response["results"]:
        results.append({
            "title": r["title"],
            "url": r["url"],
            "snippet": r["content"][:300]  # ← trim each snippet to 300 chars
        })

    return results