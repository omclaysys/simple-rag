# simple-rag

A small, clean RAG system with document upload.

**Current:** FastAPI + LangChain. Upload PDF or DOCX → exact 500-char chunks (no overlap) → local embeddings (all-MiniLM-L6-v2) → ChromaDB.

Branch: `day2/fastapi-rag-upload`

---

## How to Run

```bash
cd simple-rag
uv sync
uv run uvicorn app.main:app --reload
```

Server runs at: **http://127.0.0.1:8000**

Interactive docs: **http://127.0.0.1:8000/docs**

---

## What the API does

1. Upload one PDF or DOCX file
2. Extract text
3. Split into 500-character chunks (no overlap)
4. Embed with ChromaDB (default model: all-MiniLM-L6-v2)
5. Store in local vector database
6. Query it and get the most relevant chunks back

---

## Usage

**Upload a document:**

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@yourfile.pdf"
```

or

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@yourfile.docx"
```

**Search the RAG:**

```bash
curl "http://127.0.0.1:8000/retrieve?q=your+query+here&top_k=3"
```

---

## Requirements

- Python 3.10+
- `uv` (recommended)

---

## Clean up

```bash
rm -rf chroma_db
```

This removes the vector database.

---

MIT
