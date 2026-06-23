"""FastAPI server for the Personal Task Assistant.

Run:
    uv run uvicorn server:app --reload
"""

from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from agent.graph import graph
from agent.logger import log_event
from agent.nodes import get_current_datetime

load_dotenv()

app = FastAPI(title="LangGraph Task Assistant")


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    log_event("api_chat", query=req.query)

    state = {
        "messages": [HumanMessage(content=req.query)],
        "user_input": req.query,
        "current_date_time": get_current_datetime(),
    }

    result = graph.invoke(state)

    final_response = ""
    for msg in reversed(result["messages"]):
        tool_calls = getattr(msg, "tool_calls", None) or []
        if tool_calls:
            continue
        if hasattr(msg, "content") and msg.content:
            final_response = msg.content
            break

    log_event("api_chat_response", query=req.query, response=final_response)
    return ChatResponse(response=final_response)
