"""Graph visualization helpers.

Provides:
- mermaid source string
- optional PNG rendering (best effort)
"""

from __future__ import annotations

import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

from agent.graph import graph


def get_mermaid() -> str:
    """Return the mermaid diagram source for the compiled graph."""
    return graph.get_graph(xray=True).draw_mermaid()


def save_graph_image(output_path: str | Path = "graph.png") -> bool:
    """Try to render and save the graph as PNG.

    Returns True on success, False if rendering is not available.
    Requires optional dependencies (e.g. playwright) in some environments.
    """
    try:
        png_bytes = graph.get_graph(xray=True).draw_mermaid_png()
        Path(output_path).write_bytes(png_bytes)
        return True
    except Exception as exc:
        print(f"[visualize] Could not render PNG: {exc}")
        print("[visualize] You can paste the mermaid source into https://mermaid.live")
        return False


def print_graph() -> None:
    """Print the mermaid diagram to stdout."""
    print("\n=== LangGraph Mermaid Diagram ===")
    print(get_mermaid())
    print("=================================\n")
    print("Tip: Copy the above into https://mermaid.live to view/edit.")


if __name__ == "__main__":
    print_graph()
    save_graph_image()
    with open("graph.mmd", "w") as f:
        f.write(get_mermaid())
    print("Saved graph.mmd")
