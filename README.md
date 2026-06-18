# simple-rag

A small, clean RAG system.

This project started as a simple script and evolved on **Day 2** into a proper FastAPI service.

## Original Script (still works)

```bash
uv run python main.py
```

## Day 2: FastAPI + Document Upload

On the branch `day2/fastapi-rag-upload` we added:

- One upload endpoint that accepts **either PDF or DOCX** (one file at a time)
- Automatic text extraction, 500-char chunking, and storage in ChromaDB
- One retrieve endpoint to search the RAG index

### Run the API

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs

### Upload a document

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@myfile.pdf"
```

or

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@report.docx"
```

### Retrieve from RAG

```bash
curl "http://127.0.0.1:8000/retrieve?q=What%20is%20RAG&top_k=3"
```

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
