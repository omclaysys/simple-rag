from __future__ import annotations
from io import BytesIO
from typing import Any

from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.pdf import PyPDFium2Parser
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from docx import Document as DocxDoc

splitter = CharacterTextSplitter(separator="", chunk_size=500, chunk_overlap=0)
store: Chroma | None = None


def get_store() -> Chroma:
    global store
    if store is None:
        store = Chroma(
            collection_name="documents",
            embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            persist_directory="./chroma_db",
            collection_metadata={"hnsw:space": "cosine"},
        )
    return store


def load(name: str, data: bytes) -> list[Document]:
    n = name.lower()
    if n.endswith(".pdf"):
        return list(PyPDFium2Parser().lazy_parse(Blob.from_data(data, path=name)))
    if n.endswith(".docx"):
        txt = "\n".join(p.text for p in DocxDoc(BytesIO(data)).paragraphs).strip()
        return [Document(page_content=txt)] if txt else []
    raise ValueError("pdf/docx only")


def ingest(filename: str, data: bytes) -> int:
    docs = load(filename, data)
    if not docs:
        return 0

    chunks = splitter.split_documents(docs)
    kind = "pdf" if filename.lower().endswith(".pdf") else "docx"

    out, ids = [], []
    for d in chunks:
        t = (d.page_content or "").strip()
        if not t:
            continue
        i = len(out)
        out.append(Document(page_content=t, metadata={"source": filename, "type": kind, "chunk_index": i}))
        ids.append(f"{filename}_{i}")

    if not out:
        return 0

    get_store().add_documents(out, ids=ids)
    return len(out)


def search(q: str, k: int = 3) -> list[dict[str, Any]]:
    if not q.strip():
        return []
    pairs = get_store().similarity_search_with_score(q, k=k)
    return [{
        "text": d.page_content,
        "score": round(1 - float(dist), 4) if dist is not None else None,
        "source": (d.metadata or {}).get("source"),
        "type": (d.metadata or {}).get("type"),
        "chunk_index": (d.metadata or {}).get("chunk_index"),
    } for d, dist in pairs]
