# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from tools.vector_store import clear_store
from graph import research_graph, ResearchState
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str

@app.post("/research")
async def research(request: ResearchRequest):
    async def event_stream():
        clear_store()

        # Initial state
        state: ResearchState = {
            "query": request.query,
            "search_output": "",
            "reader_output": "",
            "final_output": "",
            "sources": [],
            "status": "starting"
        }

        # Emit start event
        yield {
            "event": "agent_update",
            "data": json.dumps({"agent": "orchestrator", "status": "done", "message": "Query planned"})
        }

        # Run each node and stream updates
        try:
            # Search
            yield {
                "event": "agent_update",
                "data": json.dumps({"agent": "search", "status": "running", "message": "Searching the web..."})
            }
            await asyncio.sleep(0)  # let the event flush

            result = await asyncio.to_thread(research_graph.invoke, state)

            yield {
                "event": "agent_update",
                "data": json.dumps({"agent": "search", "status": "done", "message": f"Found {len(result['sources'])} sources"})
            }

            yield {
                "event": "agent_update",
                "data": json.dumps({"agent": "reader", "status": "done", "message": f"Read {len(result['sources'])} pages"})
            }

            yield {
                "event": "agent_update",
                "data": json.dumps({"agent": "synthesizer", "status": "done", "message": "Answer ready"})
            }

            yield {
                "event": "final_answer",
                "data": json.dumps({
                    "answer": result["final_output"],
                    "sources": result["sources"]
                })
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_stream())

@app.get("/health")
async def health():
    return {"status": "ok"}