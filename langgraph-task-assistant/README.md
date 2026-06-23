# langgraph-task-assistant

Personal Task Assistant built as a **single AI agent** using LangGraph.

Demonstrates:
- `StateGraph`
- Custom state extending `MessagesState`
- Tool calling with `@tool`
- Prebuilt `ToolNode`
- Conditional routing (`tools_condition`)
- MessagesState for passing conversation messages to the graph
- Structured logging (JSON lines)
- Graph visualization (mermaid + optional PNG)

## Project Structure (Separation of Concerns)

```
langgraph-task-assistant/
├── agent/
│   ├── __init__.py
│   ├── state.py          # TaskAssistantState (messages + user_input + current_date_time)
│   ├── tools.py          # add_task, list_tasks, delete_task (in-memory)
│   ├── prompt.py         # System prompt
│   ├── nodes.py          # assistant node + LLM binding + routing helper
│   ├── graph.py          # StateGraph wiring: START → assistant ↔ tools → END
│   ├── logging.py        # Structured event logger (user_query, tool_*, final_response)
│   └── visualize.py      # Mermaid source + PNG export
├── main.py               # CLI entrypoint (single query only)
├── pyproject.toml
├── uv.lock
├── .env.example
└── .gitignore
```

## Setup

```bash
cd langgraph-task-assistant
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
uv sync
```

## Run

Single query only (one command = one run, no memory between runs):
```bash
uv run python main.py "add buy milk"
uv run python main.py "list my tasks"
uv run python main.py "delete task 1"
uv run python main.py "what day is it today?"
```

## Graph Visualization (Bonus)

```bash
uv run python -c "
from agent.visualize import print_graph, save_graph_image
print_graph()
save_graph_image('graph.png')
"
```

Open `graph.png` or paste the mermaid source at https://mermaid.live

## Key Concepts Implemented

- **State**: `TaskAssistantState` extends `MessagesState` with `user_input` and `current_date_time`.
- **Nodes**:
  - `assistant`: LLM decides tool use or final answer.
  - `tools`: `ToolNode` executes `add_task` / `list_tasks` / `delete_task`.
- **Edges**:
  - `START → assistant`
  - Conditional: `assistant → tools` if `tool_calls`, else `END`
  - `tools → assistant` (loop back)
- **Memory**: Full message history carried in state for follow-up questions within the same run.
- **Logging**: Every important step emits a single-line JSON event with timestamps.

## Tasks Covered (per spec, no automated test script)

- Add a task
- Add multiple tasks
- List all tasks
- Delete a task
- Ask a normal question (no tool use)
- Ask follow-up questions in the same conversation

Just type them in interactive mode or via CLI args.

## Clean Code Notes

- One responsibility per file.
- Tools are pure and easy to unit test.
- No business logic in `main.py` (it only orchestrates input/output).
- LLM and tools are wired explicitly in `nodes.py` and `graph.py`.

## Requirements

- Python 3.14+
- `uv`
- Groq API key (free tier works)

## License

MIT
