"""LLM-backed assistant node and supporting utilities."""

from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import tools_condition

from agent.logger import log_event
from agent.prompt import SYSTEM_PROMPT
from agent.tools import get_tools

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY")
if not _api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
    )

_model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

_llm = ChatGroq(
    model=_model_name,
    groq_api_key=_api_key,
    temperature=0.1,
)

_tools = get_tools()
_llm_with_tools = _llm.bind_tools(_tools)


def get_current_datetime() -> str:
    """Return a human readable current date/time string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def assistant(state: dict) -> dict:
    """Call the LLM.

    The LLM decides whether to call tools or give a final answer.
    We inject a fresh system prompt containing the current date/time.
    """
    messages = state["messages"]
    current_dt = state.get("current_date_time") or get_current_datetime()

    system_msg = SystemMessage(
        content=SYSTEM_PROMPT.format(current_date_time=current_dt)
    )

    try:
        response: AIMessage = _llm_with_tools.invoke([system_msg] + messages)
    except Exception as exc:
        log_event("llm_error", error=str(exc), user_input=state.get("user_input"))
        return {"messages": [AIMessage(content=f"I ran into an issue processing that. Please try rephrasing.")]}

    if getattr(response, "tool_calls", None):
        for tc in response.tool_calls or []:
            log_event(
                "tool_selected",
                tool=tc.get("name"),
                args=tc.get("args"),
                user_input=state.get("user_input"),
            )

    return {"messages": [response]}


# Re-export the condition for convenience in graph construction
should_continue = tools_condition
