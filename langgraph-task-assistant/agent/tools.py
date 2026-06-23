"""Task management tools (JSON-file-backed store).

Tools:
- add_task(title)
- list_tasks()
- delete_task(task_id)

Tasks persist to a JSON file so they survive restarts.
Each tool logs its execution time via the shared logger.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from agent.logger import log_event

# ---------------------------------------------------------------------------
# File-backed task store
# ---------------------------------------------------------------------------

TASKS_FILE = Path("tasks.json")


def _load_tasks() -> list[dict[str, Any]]:
    """Load tasks from the JSON file. Returns an empty list if missing/corrupt."""
    if not TASKS_FILE.exists():
        return []
    try:
        data = json.loads(TASKS_FILE.read_text())
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save_tasks(tasks: list[dict[str, Any]]) -> None:
    """Write tasks to the JSON file."""
    TASKS_FILE.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2, default=str)
    )


def _compute_next_id(tasks: list[dict[str, Any]]) -> int:
    """Return one greater than the highest existing id, or 1 if empty."""
    return max((t["id"] for t in tasks if isinstance(t.get("id"), int)), default=0) + 1


_tasks: list[dict[str, Any]] = _load_tasks()
_next_id: int = _compute_next_id(_tasks)


def _get_now() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


def _log_tool(name: str, args: dict[str, Any], start: float, result: str) -> None:
    duration_ms = int((time.perf_counter() - start) * 1000)
    log_event(
        "tool_execution",
        tool=name,
        args=args,
        duration_ms=duration_ms,
        result_preview=(result or "")[:200],
    )


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------


@tool
def add_task(title: str) -> str:
    """Add a new task.

    Args:
        title: Short, clear description of the task.

    Returns:
        Confirmation string containing the assigned numeric id.
    """
    global _tasks, _next_id
    start = time.perf_counter()

    clean_title = (title or "").strip()
    if not clean_title:
        result = "Error: title cannot be empty."
        _log_tool("add_task", {"title": title}, start, result)
        return result

    task = {
        "id": _next_id,
        "title": clean_title,
        "created_at": _get_now(),
    }
    _tasks.append(task)
    _next_id += 1
    _save_tasks(_tasks)

    result = f'Task added successfully. id={task["id"]}, title="{task["title"]}"'
    _log_tool("add_task", {"title": title}, start, result)
    return result


@tool
def list_tasks() -> str:
    """List all current tasks.

    Returns:
        JSON array of tasks, or a message if none exist.
    """
    start = time.perf_counter()

    if not _tasks:
        result = "No tasks found."
    else:
        result = json.dumps(_tasks, ensure_ascii=False, indent=2)

    _log_tool("list_tasks", {}, start, result)
    return result


@tool
def delete_task(task_id: str) -> str:
    """Delete a task by its id.

    Args:
        task_id: Numeric id of the task (as string or number).

    Returns:
        Confirmation or error message.
    """
    global _tasks
    start = time.perf_counter()

    try:
        tid = int(str(task_id).strip())
    except (ValueError, TypeError):
        result = "Error: task_id must be a number."
        _log_tool("delete_task", {"task_id": task_id}, start, result)
        return result

    before = len(_tasks)
    _tasks = [t for t in _tasks if t["id"] != tid]

    if len(_tasks) < before:
        result = f"Task {tid} deleted successfully."
    else:
        result = f"No task found with id {tid}."

    _save_tasks(_tasks)
    _log_tool("delete_task", {"task_id": tid}, start, result)
    return result


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------


def get_tools() -> list:
    """Return the list of tools for binding and ToolNode."""
    return [add_task, list_tasks, delete_task]


def reset_tasks() -> None:
    """Reset the store, clearing both memory and the file."""
    global _tasks, _next_id
    _tasks = []
    _next_id = 1
    _save_tasks(_tasks)
