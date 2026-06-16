// src/App.jsx
import { useState, useRef } from "react"

const AGENTS = ["orchestrator", "search", "reader", "synthesizer"]

const agentLabels = {
  orchestrator: "Orchestrator",
  search: "Search Agent",
  reader: "Reader Agent",
  synthesizer: "Synthesizer",
}

const statusColors = {
  idle: "#9ca3af",
  running: "#f59e0b",
  done: "#10b981",
}

export default function App() {
  const [query, setQuery] = useState("")
  const [agentStates, setAgentStates] = useState({
    orchestrator: { status: "idle", message: "" },
    search: { status: "idle", message: "" },
    reader: { status: "idle", message: "" },
    synthesizer: { status: "idle", message: "" },
  })
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [log, setLog] = useState([])
  const eventSourceRef = useRef(null)

  const addLog = (msg) => setLog((prev) => [...prev, msg])

  const resetState = () => {
    setAnswer("")
    setSources([])
    setLog([])
    setAgentStates({
      orchestrator: { status: "idle", message: "" },
      search: { status: "idle", message: "" },
      reader: { status: "idle", message: "" },
      synthesizer: { status: "idle", message: "" },
    })
  }

  const runResearch = async () => {
    if (!query.trim() || loading) return
    resetState()
    setLoading(true)

    try {
      const response = await fetch("http://localhost:8000/research", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop()

        let eventType = ""
        let dataLine = ""

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.replace("event:", "").trim()
          } else if (line.startsWith("data:")) {
            dataLine = line.replace("data:", "").trim()
            if (eventType && dataLine) {
              try {
                const payload = JSON.parse(dataLine)
                if (eventType === "agent_update") {
                  setAgentStates((prev) => ({
                    ...prev,
                    [payload.agent]: {
                      status: payload.status,
                      message: payload.message,
                    },
                  }))
                  addLog(`→ ${payload.agent}: ${payload.message}`)
                } else if (eventType === "final_answer") {
                  setAnswer(payload.answer)
                  setSources(payload.sources || [])
                  addLog("✓ Answer ready")
                } else if (eventType === "error") {
                  addLog(`✗ Error: ${payload.message}`)
                }
              } catch (e) {
                console.error("Parse error:", e)
              }
              eventType = ""
              dataLine = ""
            }
          }
        }
      }
    } catch (err) {
      addLog(`✗ Connection error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0f1117", color: "#e5e7eb", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <div style={{ borderBottom: "1px solid #1f2937", padding: "16px 24px", display: "flex", alignItems: "center", gap: "10px" }}>
        <span style={{ fontSize: "20px" }}>⚡</span>
        <span style={{ fontSize: "16px", fontWeight: 500 }}>ResearchAI</span>
        <span style={{ marginLeft: "auto", fontSize: "12px", color: "#6b7280" }}>Multi-agent research assistant</span>
      </div>

      <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "24px", display: "grid", gridTemplateColumns: "1fr 260px", gap: "20px" }}>
        
        {/* Left — main */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          
          {/* Search bar */}
          <div style={{ background: "#1a1d27", border: "1px solid #2d3748", borderRadius: "12px", padding: "12px 16px", display: "flex", gap: "10px", alignItems: "center" }}>
            <span style={{ color: "#6b7280" }}>🔍</span>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && runResearch()}
              placeholder="Ask anything — e.g. latest AI breakthroughs in 2025"
              style={{ flex: 1, background: "transparent", border: "none", outline: "none", color: "#e5e7eb", fontSize: "14px" }}
            />
            <button
              onClick={runResearch}
              disabled={loading || !query.trim()}
              style={{
                background: loading ? "#374151" : "#6366f1",
                color: "white",
                border: "none",
                borderRadius: "8px",
                padding: "8px 16px",
                fontSize: "13px",
                fontWeight: 500,
                cursor: loading ? "not-allowed" : "pointer",
                whiteSpace: "nowrap"
              }}
            >
              {loading ? "Researching..." : "▶ Research"}
            </button>
          </div>

          {/* Answer */}
          <div style={{ background: "#1a1d27", border: "1px solid #2d3748", borderRadius: "12px", padding: "20px", minHeight: "300px" }}>
            <div style={{ fontSize: "12px", fontWeight: 500, color: "#6b7280", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Answer</div>
            {answer ? (
              <div>
                <div style={{ fontSize: "14px", lineHeight: "1.8", color: "#d1d5db", whiteSpace: "pre-wrap" }}>
                  {answer}
                </div>
                {sources.length > 0 && (
                  <div style={{ marginTop: "20px" }}>
                    <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "8px", fontWeight: 500 }}>SOURCES</div>
                    {sources.map((url, i) => (
                      <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", padding: "6px 10px", background: "#111827", borderRadius: "8px", marginBottom: "6px" }}>
                        <span style={{ fontSize: "11px", color: "#6b7280" }}>🔗</span>
                        <a href={url} target="_blank" rel="noreferrer" style={{ fontSize: "12px", color: "#818cf8", textDecoration: "none", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{url}</a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ color: "#4b5563", fontSize: "14px", marginTop: "40px", textAlign: "center" }}>
                {loading ? "Agents are working..." : "Your answer will appear here"}
              </div>
            )}
          </div>
        </div>

        {/* Right — sidebar */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          
          {/* Agent activity */}
          <div style={{ background: "#1a1d27", border: "1px solid #2d3748", borderRadius: "12px", padding: "16px" }}>
            <div style={{ fontSize: "11px", fontWeight: 500, color: "#6b7280", marginBottom: "14px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Agent Activity</div>
            {AGENTS.map((agent) => {
              const state = agentStates[agent]
              const color = statusColors[state.status]
              return (
                <div key={agent} style={{ marginBottom: "14px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                    <div style={{
                      width: "8px", height: "8px", borderRadius: "50%", background: color,
                      boxShadow: state.status === "running" ? `0 0 6px ${color}` : "none",
                      animation: state.status === "running" ? "pulse 1s infinite" : "none"
                    }} />
                    <span style={{ fontSize: "12px", color: "#e5e7eb", flex: 1 }}>{agentLabels[agent]}</span>
                    <span style={{ fontSize: "11px", color }}>
                      {state.status === "idle" ? "waiting" : state.status}
                    </span>
                  </div>
                  {state.message && (
                    <div style={{ fontSize: "11px", color: "#6b7280", paddingLeft: "16px" }}>{state.message}</div>
                  )}
                  <div style={{ height: "2px", background: "#1f2937", borderRadius: "2px", marginTop: "6px" }}>
                    <div style={{
                      height: "100%", borderRadius: "2px", background: color,
                      width: state.status === "done" ? "100%" : state.status === "running" ? "60%" : "0%",
                      transition: "width 0.4s ease"
                    }} />
                  </div>
                </div>
              )
            })}
          </div>

          {/* Log */}
          <div style={{ background: "#1a1d27", border: "1px solid #2d3748", borderRadius: "12px", padding: "16px" }}>
            <div style={{ fontSize: "11px", fontWeight: 500, color: "#6b7280", marginBottom: "10px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Live Log</div>
            <div style={{ fontFamily: "monospace", fontSize: "11px", display: "flex", flexDirection: "column", gap: "4px", maxHeight: "180px", overflowY: "auto" }}>
              {log.length === 0 ? (
                <span style={{ color: "#4b5563" }}>Waiting for query...</span>
              ) : (
                log.map((line, i) => (
                  <span key={i} style={{ color: line.startsWith("✓") ? "#10b981" : line.startsWith("✗") ? "#ef4444" : "#6b7280" }}>{line}</span>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1 } 50% { opacity: 0.4 } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
      `}</style>
    </div>
  )
}