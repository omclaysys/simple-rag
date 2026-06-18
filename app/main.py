"""FastAPI application for document upload + RAG retrieval.

Design goals:
- One endpoint for both PDF and DOCX (single file at a time)
- Clean separation of concerns
- Reuses the existing simple chunking + ChromaDB logic
- No LangChain
- Easy to test and maintain
"""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends

from app.extract import extract_text
from app.chunk import chunk_text
from app.store import get_client, get_collection, add_chunks, query as rag_query


def get_rag_collection():
    """FastAPI dependency that provides the ChromaDB collection.

    This makes the endpoints much easier to test (we can override the dependency).
    """
    client = get_client()
    return get_collection(client)


app = FastAPI(
    title="Simple RAG API",
    description="Upload a PDF or DOCX file → text is extracted, chunked, embedded and stored. "
                "Use /retrieve to search the knowledge base.",
    version="0.2.0",
)


def _is_supported_file(filename: str) -> bool:
    lower = filename.lower()
    return lower.endswith(".pdf") or lower.endswith(".docx")


@app.post("/upload")
async def upload_document(
    file: Annotated[UploadFile, File(description="One PDF or DOCX file")],
    collection=Depends(get_rag_collection),
):
    """Upload one document (PDF or DOCX).

    The file is processed synchronously for simplicity:
    - Extract text
    - Split into 500-character chunks (no overlap)
    - Embed and store in ChromaDB
    """
    if not file.filename or not _is_supported_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf and .docx files are supported.",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(content) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    try:
        raw_text = extract_text(file.filename, content)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Failed to extract text: {str(exc)}"
        ) from exc

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in the document")

    chunks = chunk_text(raw_text)

    source_type = "pdf" if file.filename.lower().endswith(".pdf") else "docx"
    add_chunks(
        collection=collection,
        chunks=chunks,
        source=file.filename,
        source_type=source_type,
    )

    return {
        "filename": file.filename,
        "chunks_added": len(chunks),
        "message": "Document processed and added to the knowledge base",
    }


@app.get("/retrieve")
async def retrieve(
    q: Annotated[str, Query(min_length=1, description="Your search query")],
    top_k: Annotated[int, Query(ge=1, le=20, description="Number of results to return")] = 3,
    collection=Depends(get_rag_collection),
):
    """Search the RAG index for the most relevant chunks."""
    results = rag_query(collection, q, top_k=top_k)
    return {
        "query": q,
        "top_k": top_k,
        "results": results,
    }


@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {"status": "ok"}
