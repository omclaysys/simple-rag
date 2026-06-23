"""Structured logging for the agent (single-line JSON events)."""

import json
from datetime import datetime, timezone
from typing import Any


def log_event(event: str, **fields: Any) -> None:
    """Emit one structured log line.

    Events we emit:
    - user_query
    - tool_selected
    - tool_execution
    - final_response
    """
    payload: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    # Print directly for immediate CLI output (easy to grep/json parse)
    print(json.dumps(payload, ensure_ascii=False, default=str))
