# agents/reader.py
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from tools.fetch_url import fetch_url as fetch_url_fn
from tools.parse_pdf import parse_pdf as parse_pdf_fn
from tools.vector_store import save_to_store
from config import GROQ_API_KEY
import json

@tool
def fetch_url(url: str) -> str:
    """Fetch and read the full content of a webpage URL."""
    result = fetch_url_fn(url)
    save_to_store(
        content=result["content"],
        metadata={"source": result["url"], "title": result["title"], "agent": "reader"},
        doc_id=f"reader_{url[:40]}"
    )
    return json.dumps(result, indent=2)

@tool
def parse_pdf(url: str) -> str:
    """Extract and read text from a PDF at a given URL."""
    result = parse_pdf_fn(url)
    save_to_store(
        content=result["content"],
        metadata={"source": result["source"], "agent": "reader"},
        doc_id=f"pdf_{url[:40]}"
    )
    return json.dumps(result, indent=2)

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
reader_agent = create_react_agent(llm, tools=[fetch_url, parse_pdf])

def run_reader_agent(urls: list[str]) -> dict:
    """Read the full content of a list of URLs."""
    system = "You are a research assistant. Search for the query and briefly summarize the top results in 3-4 sentences. List the source URLs."

    url_list = "\n".join(urls[:3])  # limit to 3 URLs to save tokens

    result = reader_agent.invoke({
        "messages": [
            SystemMessage(content=system),
            HumanMessage(content=f"Read and summarize these sources:\n{url_list}")
        ]
    })

    return {
        "agent": "reader",
        "output": result["messages"][-1].content
    }