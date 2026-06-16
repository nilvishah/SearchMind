# agents/synthesizer.py
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from tools.vector_store import search_store as search_store_fn
from config import GROQ_API_KEY
import json

@tool
def search_store(query: str) -> str:
    """Search everything gathered so far by the other agents semantically."""
    results = search_store_fn(query, n_results=5)
    return json.dumps(results, indent=2)

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
synthesizer_agent = create_react_agent(llm, tools=[search_store])

def run_synthesizer_agent(query: str, search_summary: str, reader_summary: str) -> dict:
    """Synthesize everything into a final cited answer."""
    system = """You are a research synthesis specialist. You have access to a vector 
    store containing everything the search and reader agents have gathered. 
    Your job is to write a comprehensive, well-structured answer with citations.
    Always end with a ## Sources section listing every URL referenced."""

    context = f"""
Original question: {query}

What the search agent found:
{search_summary}

What the reader agent found:
{reader_summary}

Now search the store for any additional relevant details, then write the final answer.
"""

    result = synthesizer_agent.invoke({
        "messages": [
            SystemMessage(content=system),
            HumanMessage(content=context)
        ]
    })

    return {
        "agent": "synthesizer",
        "output": result["messages"][-1].content
    }