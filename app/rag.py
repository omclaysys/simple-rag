from __future__ import annotations
from io import BytesIO
from threading import Lock
from typing import Any
import os

from langchain_core.documents import Document
from langchain_core.documents.base import Blob
from langchain_community.document_loaders.parsers.pdf import PyPDFium2Parser
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from docx import Document as DocxDoc

chunksplitter = CharacterTextSplitter(separator="", chunk_size=500, chunk_overlap=0)

vectorstore: Chroma | None = None
llm = None
dblock = Lock()


def getvectorstore() -> Chroma:
    global vectorstore
    if vectorstore is None:
        vectorstore = Chroma(
            collection_name="documents",
            embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            persist_directory="./chroma_db",
            collection_metadata={"hnsw:space": "cosine"},
        )
    return vectorstore


def loaddocuments(filename: str, data: bytes) -> list[Document]:
    name = filename.lower()
    if name.endswith(".pdf"):
        blob = Blob.from_data(data, path=filename)
        return list(PyPDFium2Parser().lazy_parse(blob))
    if name.endswith(".docx"):
        doc = DocxDoc(BytesIO(data))
        text = "\n".join(p.text for p in doc.paragraphs).strip()
        return [Document(page_content=text)] if text else []
    raise ValueError("Only PDF and DOCX supported")


def ingest(filename: str, data: bytes) -> int:
    docs = loaddocuments(filename, data)
    if not docs:
        return 0

    chunks = chunksplitter.split_documents(docs)
    doctype = "pdf" if filename.lower().endswith(".pdf") else "docx"

    final = []
    ids = []
    for chunk in chunks:
        text = (chunk.page_content or "").strip()
        if not text:
            continue
        index = len(final)
        final.append(Document(
            page_content=text,
            metadata={"source": filename, "type": doctype, "chunkindex": index}
        ))
        ids.append(f"{filename}-{index}")

    if not final:
        return 0

    with dblock:
        getvectorstore().add_documents(final, ids=ids)
    return len(final)


def search(query: str, topk: int = 3) -> list[dict[str, Any]]:
    if not query or not query.strip():
        return []

    with dblock:
        results = getvectorstore().similarity_search_with_score(query, k=topk)

    output = []
    for doc, distance in results:
        meta = doc.metadata or {}
        output.append({
            "text": doc.page_content,
            "score": round(1 - float(distance), 4) if distance is not None else None,
            "source": meta.get("source"),
            "type": meta.get("type"),
            "chunkindex": meta.get("chunkindex"),
        })
    return output


def getllm():
    global llm
    if llm is None:
        apikey = os.getenv("GROQ_API_KEY")
        if not apikey:
            raise RuntimeError("GROQ_API_KEY is not set")
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=apikey,
            temperature=0.2,
        )
    return llm


prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer based on the context provided. If not found, say you don't know."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])


def ask(question: str) -> dict:
    """Simple RAG: retrieve chunks, pass to LLM."""
    if not question or not question.strip():
        return {"question": question, "answer": "", "sources": []}

    results = search(question, topk=3)
    context = "\n\n".join(r["text"] for r in results)

    chain = prompt | getllm()
    answer = chain.invoke({"context": context, "question": question}).content

    return {
        "question": question,
        "answer": answer or "No answer generated.",
        "sources": results,
    }
