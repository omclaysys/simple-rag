# simple-rag

A tiny, clean RAG demo in one file.

**What it does:**
1. Reads `sample.txt`
2. Splits the text into simple fixed-size chunks of 500 characters (no overlap)
3. Embeds the chunks using ChromaDB (default model: all-MiniLM-L6-v2)
4. Stores them in a local ChromaDB collection
5. Runs a hardcoded query and prints the top 3 most relevant chunks with similarity scores

No CLI. No extra frameworks. Just `uv run python main.py`.

## Requirements

- Python 3.10+
- `uv` (recommended)

## How to Run

```bash
cd simple-rag

# First time only (installs chromadb + downloads embedding model)
uv sync

# Run the demo
uv run python main.py
```

That's it.

On first run it will download the ~80MB sentence-transformers model.

## What you will see

- "Loaded X chunk(s)"
- The query being used
- Top 3 chunks with similarity scores (higher = better match)

## Files

| File          | Purpose                              |
|---------------|--------------------------------------|
| `main.py`     | The entire demo (hardcoded)          |
| `sample.txt`  | The text that gets chunked + embedded|
| `pyproject.toml` | Dependencies (chromadb + ruff dev) |
| `chroma_db/`  | Persistent ChromaDB data (created on run) |

## Current hardcoded settings (in main.py)

- Query: `"What is RAG and how does chunking help?"`
- Chunk size: 500 characters (simple fixed-size split, **no overlap**)
- Top results: 3

Chunking is dead simple:
```python
for i in range(0, len(text), 500):
    chunk = text[i : i + 500].strip()
    if chunk:
        chunks.append(chunk)
```

To change the question or behavior, just edit `main.py`.

## Clean up

To start fresh:

```bash
rm -rf chroma_db
```

## Notes

- Uses `PersistentClient` → data stays on disk in `./chroma_db`
- Chroma automatically handles embeddings with its default model
- This is intentionally the simplest possible working RAG loop

MIT
