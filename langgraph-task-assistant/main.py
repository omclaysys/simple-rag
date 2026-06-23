"""CLI entrypoint for the Personal Task Assistant.

Usage:
    uv run python main.py "add buy groceries"
    uv run python main.py "list all my tasks"
    uv run python main.py "delete task 1"
    uv run python main.py "what day is it today?"

This runs the compiled LangGraph agent for a single query.
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent.graph import graph
from agent.logger import log_event
from agent.nodes import get_current_datetime

load_dotenv()


def run_query(query: str) -> str:
    """Run one user query against the graph and return the final text response."""
    log_event("user_query", query=query)

    state = {
        "messages": [HumanMessage(content=query)],
        "user_input": query,
        "current_date_time": get_current_datetime(),
    }

    result = graph.invoke(state)

    # Find the last AIMessage that is not a tool call (the final response)
    final_response = ""
    for msg in reversed(result["messages"]):
        # Skip messages that contain tool_calls (even if content is non-empty)
        tool_calls = getattr(msg, "tool_calls", None) or []
        if tool_calls:
            continue
        if hasattr(msg, "content") and msg.content:
            final_response = msg.content
            break

    log_event("final_response", response=final_response)
    return final_response


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python main.py \"your query here\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    response = run_query(query)
    print(f"\nAssistant: {response}")


if __name__ == "__main__":
    main()
