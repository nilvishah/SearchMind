# tools/fetch_url.py
import requests
from bs4 import BeautifulSoup

def fetch_url(url: str) -> dict:
    """
    Fetch a webpage and return clean text content.
    Returns title, url, and the full readable text.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else "No title"
        text = soup.get_text(separator="\n", strip=True)

        # Trim to first 3000 chars so we don't flood the LLM context
        text = text[:3000]

        return {
            "url": url,
            "title": title,
            "content": text
        }

    except Exception as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Failed to fetch: {str(e)}"
        }