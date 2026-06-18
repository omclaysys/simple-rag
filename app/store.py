"""ChromaDB storage helpers for the RAG demo.

Clean wrapper around the existing simple pattern:
- One collection
- Store chunks with basic metadata
- Query and return text + scores
"""

from __future__ import annotations

from typing import Any

import chromadb
from chromadb.utils import embedding_functions

DEFAULT_COLLECTION = "documents"
CHROMA_PATH = "./chroma_db"


def get_client(path: str = CHROMA_PATH) -> chromadb.PersistentClient:
    """Return a persistent Chroma client."""
    return chromadb.PersistentClient(path=path)


def get_collection(
    client: chromadb.PersistentClient,
    name: str = DEFAULT_COLLECTION,
) -> chromadb.Collection:
    """Get or create the documents collection with cosine space."""
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=embedding_functions.DefaultEmbeddingFunction(),
    )


def add_chunks(
    collection: chromadb.Collection,
    chunks: list[str],
    source: str,
    source_type: str,
) -> None:
    """Add chunks to the collection with metadata.

    Each chunk gets an id like: {source}_{index}
    """
    if not chunks:
        return

    ids = [f"{source}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": source, "type": source_type, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)


def query(
    collection: chromadb.Collection,
    text: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Query the collection and return clean results.

    Returns list of dicts with: text, score, source, type, chunk_index
    Score is converted to similarity (1 - distance).
    """
    if not text.strip():
        return []

    res = collection.query(query_texts=[text], n_results=top_k)

    docs = res.get("documents", [[]])[0] or []
    dists = res.get("distances", [[]])[0] or []
    metas = res.get("metadatas", [[]])[0] or []

    results: list[dict[str, Any]] = []
    for doc, dist, meta in zip(docs, dists, metas):
        score = round(1 - float(dist), 4) if dist is not None else None
        results.append(
            {
                "text": doc,
                "score": score,
                "source": meta.get("source"),
                "type": meta.get("type"),
                "chunk_index": meta.get("chunk_index"),
            }
        )
    return results
