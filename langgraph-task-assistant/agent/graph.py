"""Build and compile the LangGraph StateGraph for the task assistant.

Graph structure:
    START --> assistant
    assistant --(has tool_calls)--> tools
    tools --> assistant
    assistant --(no tool_calls)--> END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.nodes import assistant, should_continue
from agent.state import TaskAssistantState
from agent.tools import get_tools


def build_graph():
    """Create the compiled graph."""
    graph_builder = StateGraph(TaskAssistantState)

    # Nodes
    graph_builder.add_node("assistant", assistant)
    graph_builder.add_node("tools", ToolNode(get_tools()))

    # Edges
    graph_builder.add_edge(START, "assistant")
    graph_builder.add_conditional_edges(
        "assistant",
        should_continue,
        {"tools": "tools", END: END},
    )
    graph_builder.add_edge("tools", "assistant")

    # Compile (no checkpointer for this demo)
    return graph_builder.compile()


# Singleton compiled graph for direct import
graph = build_graph()
