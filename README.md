```markdown
# SearchMind 🔍

> A multi-agent AI research assistant that answers any question with cited, live sources, like having a team of researchers working in parallel for you.

## What is this?

Most AI tools answer from stale training data with no sources. SearchMind fixes that by running multiple specialized AI agents in parallel — one searches the live web, one reads full pages, one synthesizes everything into a cited answer. All in under 30 seconds.

Think Perplexity AI — but built from scratch with a full multi-agent orchestration layer.

---

## How it works

```
User Query
    ↓
Orchestrator Agent  →  breaks query into a research plan
    ↓
Search Agent        →  hits the live web via Tavily API
Reader Agent        →  scrapes and reads full page content
    ↓
Shared Vector Store →  all findings stored semantically in ChromaDB
    ↓
Synthesizer Agent   →  merges everything into a cited answer
    ↓
Streamed to UI in real time via Server-Sent Events
```

Each agent operates as an autonomous ReAct loop — it reasons over tool outputs, retries on failure, and writes results to a shared state before passing off to the next agent.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Agent Orchestration | LangGraph |
| LLM | Groq (Llama 3.3 70B) |
| Web Search | Tavily API |
| Vector Store | ChromaDB |
| Backend | FastAPI + SSE Streaming |
| Frontend | React + Vite |
| PDF Parsing | PyMuPDF |
| Web Scraping | BeautifulSoup4 |

---

## Features

- **Multi-agent orchestration** — specialized agents coordinate via shared LangGraph state
- **Live web search** — answers use real sources from the web, not stale training data
- **Full page reading** — reader agent scrapes beyond snippets to get full content
- **PDF support** — can extract and reason over PDF documents
- **Cited answers** — every claim is traced back to a source URL
- **Real-time agent activity** — watch each agent fire live in the UI sidebar
- **Semantic memory** — ChromaDB stores all findings for cross-agent retrieval
- **Streaming** — answer streams to the frontend as it's generated

---

## Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/nilvishah/SearchMind.git
cd SearchMind
```

### 2. Set up the backend
```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your API keys
Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Get your keys here — both are free:
- Groq: https://console.groq.com
- Tavily: https://app.tavily.com

### 4. Start the backend
```bash
uvicorn main:app --reload --port 8000
```

### 5. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and start researching.

---

## Project Structure

```
SearchMind/
├── main.py              # FastAPI server + SSE endpoint
├── graph.py             # LangGraph orchestration
├── config.py            # Environment variables
├── agents/
│   ├── search.py        # Search agent (ReAct loop)
│   ├── reader.py        # Reader agent (ReAct loop)
│   └── synthesizer.py   # Synthesizer agent (ReAct loop)
├── tools/
│   ├── web_search.py    # Tavily web search
│   ├── fetch_url.py     # BeautifulSoup scraper
│   ├── parse_pdf.py     # PyMuPDF PDF extractor
│   └── vector_store.py  # ChromaDB save + search
└── frontend/            # React + Vite UI
```

---

## Architecture decisions

**Why LangGraph over LangChain?** LangGraph gives explicit control over the agent state graph — you can see exactly what each node receives and emits. Better for debugging and extending.

**Why separate agents instead of one big prompt?** Each agent has a focused context window. The search agent only sees search results. The synthesizer only sees summaries. This reduces hallucination and keeps each LLM call cheap and fast.

**Why ChromaDB for shared state?** Agents need to share findings semantically, not just by passing strings. ChromaDB lets the synthesizer ask "what did we find about X?" and get the most relevant chunks — even if those exact words weren't used.

**Why SSE over WebSockets?** SSE is simpler for unidirectional streaming (server → client). No handshake overhead, works over standard HTTP, and is natively supported in browsers with `EventSource`.

---

## What I'd add with more time

- [ ] Parallel agent execution (search + reader simultaneously)
- [ ] Follow-up question support with conversation memory  
- [ ] Export answer as PDF or Markdown
- [ ] Support for uploading your own documents
- [ ] Rate limiting and request queuing

---