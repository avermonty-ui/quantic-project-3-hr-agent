from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from fastapi.responses import HTMLResponse
from app.agent import run_agent


app = FastAPI(
    title="Quantic Project 3 HR Agent",
    description="Agentic HR policy assistant with RAG and MCP-style tools.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str
    employee_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    snippets: List[Dict[str, Any]]
    tool_trace: List[Dict[str, Any]]

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Northstar PeopleOps Assistant</title>
        <style>
            :root {
                --bg: #f5f7fb;
                --card: #ffffff;
                --primary: #243b6b;
                --primary-light: #edf2ff;
                --accent: #4f7cff;
                --text: #1f2937;
                --muted: #6b7280;
                --border: #d8dee9;
                --success: #12805c;
                --code-bg: #111827;
            }

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Inter, Arial, sans-serif;
                background: linear-gradient(135deg, #eef3ff 0%, #f9fafb 45%, #eefbf6 100%);
                color: var(--text);
            }

            .shell {
                max-width: 1180px;
                margin: 0 auto;
                padding: 32px 24px 48px;
            }

            .hero {
                display: grid;
                grid-template-columns: 1.2fr 0.8fr;
                gap: 24px;
                align-items: stretch;
                margin-bottom: 24px;
            }

            .hero-card, .info-card, .chat-card {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid var(--border);
                border-radius: 20px;
                box-shadow: 0 18px 45px rgba(31, 41, 55, 0.08);
            }

            .hero-card {
                padding: 32px;
            }

            .eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 10px;
                border-radius: 999px;
                background: var(--primary-light);
                color: var(--primary);
                font-size: 13px;
                font-weight: 700;
                margin-bottom: 18px;
            }

            .logo-dot {
                width: 9px;
                height: 9px;
                border-radius: 50%;
                background: var(--accent);
                display: inline-block;
            }

            h1 {
                margin: 0;
                font-size: 42px;
                line-height: 1.05;
                letter-spacing: -0.04em;
                color: var(--primary);
            }

            .subtitle {
                margin-top: 16px;
                font-size: 17px;
                color: var(--muted);
                max-width: 720px;
            }

            .info-card {
                padding: 24px;
            }

            .info-card h2 {
                margin: 0 0 12px;
                font-size: 18px;
                color: var(--primary);
            }

            .capability {
                display: flex;
                gap: 10px;
                margin: 14px 0;
                color: var(--muted);
                font-size: 14px;
            }

            .check {
                color: var(--success);
                font-weight: 900;
            }

            .chat-card {
                display: grid;
                grid-template-columns: 420px 1fr;
                overflow: hidden;
                min-height: 650px;
            }

            .panel {
                padding: 28px;
                border-right: 1px solid var(--border);
                background: #fbfcff;
            }

            .panel h2, .response-panel h2 {
                margin: 0 0 8px;
                color: var(--primary);
            }

            .helper {
                margin: 0 0 22px;
                color: var(--muted);
                font-size: 14px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 700;
                font-size: 14px;
                color: #374151;
            }

            input, textarea, select {
                width: 100%;
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 12px 14px;
                margin-bottom: 16px;
                font-size: 14px;
                background: #ffffff;
                color: var(--text);
            }

            textarea {
                resize: vertical;
                min-height: 130px;
            }

            button {
                width: 100%;
                border: 0;
                border-radius: 12px;
                padding: 13px 18px;
                background: var(--accent);
                color: white;
                font-size: 15px;
                font-weight: 800;
                cursor: pointer;
                box-shadow: 0 10px 20px rgba(79, 124, 255, 0.25);
            }

            button:hover {
                background: #3d68e8;
            }

            .demo-buttons {
                display: grid;
                gap: 10px;
                margin-top: 20px;
            }

            .demo-buttons button {
                background: #ffffff;
                color: var(--primary);
                border: 1px solid var(--border);
                box-shadow: none;
                text-align: left;
                font-weight: 700;
            }

            .demo-buttons button:hover {
                background: var(--primary-light);
            }

            .response-panel {
                padding: 28px;
                background: #ffffff;
            }

            .answer-box {
                border: 1px solid var(--border);
                border-radius: 16px;
                background: #f9fafb;
                padding: 20px;
                min-height: 120px;
                white-space: pre-wrap;
                margin-bottom: 18px;
            }

            .section-title {
                margin-top: 22px;
                margin-bottom: 10px;
                color: var(--primary);
                font-size: 15px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }

            pre {
                background: var(--code-bg);
                color: #e5e7eb;
                border-radius: 16px;
                padding: 18px;
                overflow-x: auto;
                white-space: pre-wrap;
                max-height: 360px;
                font-size: 13px;
            }

            .source-list {
                display: grid;
                gap: 10px;
            }

            .source-card {
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 14px;
                background: #ffffff;
            }

            .source-card strong {
                color: var(--primary);
            }

            .source-card span {
                display: block;
                color: var(--muted);
                font-size: 13px;
                margin-top: 4px;
            }

            .status {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                color: var(--success);
                font-weight: 800;
                margin-bottom: 12px;
            }

            @media (max-width: 900px) {
                .hero, .chat-card {
                    grid-template-columns: 1fr;
                }

                .panel {
                    border-right: 0;
                    border-bottom: 1px solid var(--border);
                }

                h1 {
                    font-size: 34px;
                }
            }
        </style>
    </head>
    <body>
        <div class="shell">
            <section class="hero">
                <div class="hero-card">
                    <div class="eyebrow">
                        <span class="logo-dot"></span>
                        Northstar People Operations
                    </div>
                    <h1>Northstar PeopleOps Assistant</h1>
                    <p class="subtitle">
                        A policy-grounded HR operations assistant that retrieves company policy evidence,
                        checks synthetic employee records, and shows the operational tool trace behind each answer.
                    </p>
                </div>

                <div class="info-card">
                    <h2>System Capabilities</h2>
                    <div class="capability"><span class="check">✓</span><span>Policy RAG with cited HR sources</span></div>
                    <div class="capability"><span class="check">✓</span><span>MCP-style tool calls over mock HR data</span></div>
                    <div class="capability"><span class="check">✓</span><span>PTO, remote work, and benefits workflows</span></div>
                    <div class="capability"><span class="check">✓</span><span>Visible operational trace for grading and auditability</span></div>
                </div>
            </section>

            <section class="chat-card">
                <div class="panel">
                    <div class="status">
                        <span class="logo-dot"></span>
                        Demo environment online
                    </div>

                    <h2>Ask the HR Agent</h2>
                    <p class="helper">
                        Use employee IDs like E1001 or names like Avery Kim, Maya Patel, Leo Martinez, or Nina Chen. The assistant will combine policy retrieval
                        with mock structured HR data where appropriate.
                    </p>

                    <label for="employee_id">Employee ID or Name</label>
                    <input id="employee_id" value="E1001" />

                    <label for="message">Message</label>
                    <textarea id="message">Can employee E1001 take three days of PTO next week?</textarea>

                    <button onclick="sendChat()">Run HR Workflow</button>

                    <div class="demo-buttons">
                        <button onclick="loadDemo('pto')">Demo 1: PTO request guidance</button>
                        <button onclick="loadDemo('remote')">Demo 2: Extended remote work review</button>
                        <button onclick="loadDemo('benefits')">Demo 3: Benefits eligibility check</button>
                        <button onclick="loadDemo('expense')">Policy Q&A: Home office chair reimbursement</button>
                    </div>
                </div>

                <div class="response-panel">
                    <h2>Agent Response</h2>
                    <p class="helper">
                        Final answer, supporting sources, and concise tool-call trace appear below.
                    </p>

                    <div id="answer" class="answer-box">No response yet.</div>

                    <div class="section-title">Citations</div>
                    <div id="citations" class="source-list"></div>

                    <div class="section-title">Tool Trace</div>
                    <pre id="trace">No tool calls yet.</pre>

                    <div class="section-title">Raw JSON</div>
                    <pre id="raw">No response yet.</pre>
                </div>
            </section>
        </div>

        <script>
            function loadDemo(type) {
                const employee = document.getElementById("employee_id");
                const message = document.getElementById("message");

                if (type === "pto") {
                   employee.value = "Avery Kim";
                   message.value = "Can Avery Kim take three days of PTO next week?";
}

                if (type === "remote") {
                   employee.value = "Maya Patel";
                   message.value = "Can Maya Patel work remotely from another state for six weeks?";
}

                if (type === "benefits") {
                    employee.value = "E1003";
                    message.value = "Is employee E1003 eligible for medical, dental, and vision benefits?";
                }

                if (type === "expense") {
                    employee.value = "E1001";
                    message.value = "Can a remote employee expense a home office chair?";
                }
            }

            async function sendChat() {
                const message = document.getElementById("message").value;
                const employee_id = document.getElementById("employee_id").value || null;

                const answerBox = document.getElementById("answer");
                const citationsBox = document.getElementById("citations");
                const traceBox = document.getElementById("trace");
                const rawBox = document.getElementById("raw");

                answerBox.textContent = "Running policy retrieval and HR tool workflow...";
                citationsBox.innerHTML = "";
                traceBox.textContent = "Loading...";
                rawBox.textContent = "Loading...";

                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        message: message,
                        employee_id: employee_id
                    })
                });

                const data = await res.json();

                answerBox.textContent = data.answer || "No answer returned.";

                citationsBox.innerHTML = "";
                if (data.citations && data.citations.length > 0) {
                    data.citations.forEach((citation) => {
                        const card = document.createElement("div");
                        card.className = "source-card";
                        card.innerHTML = `
                            <strong>${citation.title}</strong>
                            <span>Section: ${citation.section}</span>
                            <span>Source: ${citation.source_path}</span>
                        `;
                        citationsBox.appendChild(card);
                    });
                } else {
                    citationsBox.textContent = "No citations returned.";
                }

                traceBox.textContent = JSON.stringify(data.tool_trace, null, 2);
                rawBox.textContent = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """

@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "app": "quantic-project-3-hr-agent",
        "mcp_tools": "available",
        "rag_index": "available",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = run_agent(
        message=request.message,
        employee_id=request.employee_id,
    )

    return ChatResponse(**result)