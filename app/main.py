from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

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