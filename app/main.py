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
        <title>Quantic Project 3 HR Agent</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.5;
            }
            textarea, input {
                width: 100%;
                padding: 10px;
                margin-top: 8px;
                margin-bottom: 16px;
                font-size: 14px;
            }
            button {
                padding: 10px 16px;
                font-size: 14px;
                cursor: pointer;
            }
            pre {
                background: #f4f4f4;
                padding: 16px;
                white-space: pre-wrap;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <h1>Quantic Project 3 HR Agent</h1>
        <p>Ask an HR policy or workflow question. Try employee IDs like E1001, E1002, E1003, or E1004.</p>

        <label>Employee ID optional:</label>
        <input id="employee_id" value="E1001" />

        <label>Message:</label>
        <textarea id="message" rows="5">Can employee E1001 take three days of PTO next week?</textarea>

        <button onclick="sendChat()">Ask HR Agent</button>

        <h2>Response</h2>
        <pre id="response">No response yet.</pre>

        <script>
            async function sendChat() {
                const message = document.getElementById("message").value;
                const employee_id = document.getElementById("employee_id").value || null;

                const responseBox = document.getElementById("response");
                responseBox.textContent = "Loading...";

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
                responseBox.textContent = JSON.stringify(data, null, 2);
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