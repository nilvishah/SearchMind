# graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.search import run_search_agent
from agents.reader import run_reader_agent
from agents.synthesizer import run_synthesizer_agent
from tools.vector_store import clear_store
import re

# This is the shared state passed between all nodes
class ResearchState(TypedDict):
    query: str
    search_output: str
    reader_output: str
    final_output: str
    sources: list[str]
    status: str

def orchestrator_node(state: ResearchState) -> ResearchState:
    """Plans the research — just sets status for now, agents do the work."""
    return {**state, "status": "searching"}

def search_node(state: ResearchState) -> ResearchState:
    result = run_search_agent(state["query"])
    # Extract URLs from the output
    urls = re.findall(r'https?://[^\s\)\"\,\>]+', result["output"])
    # Also get URLs from the vector store directly via search
    urls = list(set(urls))[:3]  # deduplicate
    return {
        **state,
        "search_output": result["output"],
        "sources": urls,
        "status": "reading"
    }

def reader_node(state: ResearchState) -> ResearchState:
    urls = state.get("sources", [])
    if not urls:
        return {**state, "reader_output": "No URLs to read.", "status": "synthesizing"}
    result = run_reader_agent(urls)
    return {**state, "reader_output": result["output"], "status": "synthesizing"}

def synthesizer_node(state: ResearchState) -> ResearchState:
    result = run_synthesizer_agent(
        state["query"],
        state["search_output"],
        state["reader_output"]
    )
    return {**state, "final_output": result["output"], "status": "done"}

# Wire up the graph
def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("search", search_node)
    graph.add_node("reader", reader_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "search")
    graph.add_edge("search", "reader")
    graph.add_edge("reader", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()

research_graph = build_graph()