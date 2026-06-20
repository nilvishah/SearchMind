# agents/search.py
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from tools.web_search import web_search as web_search_fn
from config import GROQ_API_KEY
from tools.vector_store import save_to_store
import json

# Wrap our functions as LangChain tools
@tool
def search_web(query: str) -> str:
    """Search the live web for current information on a topic. Use this to find recent sources."""
    results = web_search_fn(query, max_results=5)
    # Save each result to the vector store
    for i, r in enumerate(results):
        save_to_store(
            content=r["snippet"],
            metadata={"source": r["url"], "title": r["title"], "agent": "search"},
            doc_id=f"search_{query[:20]}_{i}"
        )
    return json.dumps(results, indent=2)

# Initialize the LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

# Create the agent with the search tool
search_agent = create_react_agent(llm, tools=[search_web])

def run_search_agent(query: str) -> dict:
    """
    Run the search agent on a research query.
    Returns sources found and a summary.
    """
    system = """You are a research search specialist. Search for the query using different 
    keywords to get comprehensive results. Summarize findings and list key sources."""

    result = search_agent.invoke({
        "messages": [
            SystemMessage(content=system),
            HumanMessage(content=f"Find sources for: {query}")
        ]
    })

    # Get the final message from the agent
    final_message = result["messages"][-1].content

    return {
        "agent": "search",
        "query": query,
        "output": final_message
    }