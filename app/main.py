from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from typing import Annotated

from app.rag import ingest, search

app = FastAPI()

def is_supported(name: str) -> bool:
    n = name.lower()
    return n.endswith(".pdf") or n.endswith(".docx")

@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()]):
    if not file.filename or not is_supported(file.filename):
        raise HTTPException(400, "pdf/docx only")
    data = await file.read()
    if not data:
        raise HTTPException(400, "empty")
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "too big")
    try:
        n = ingest(file.filename, data)
    except Exception as e:
        raise HTTPException(400, str(e))
    if n == 0:
        raise HTTPException(400, "no text")
    return {"filename": file.filename, "chunks_added": n}

@app.get("/retrieve")
async def retrieve(q: Annotated[str, Query(min_length=1)], top_k: int = 3):
    return {"query": q, "top_k": top_k, "results": search(q, top_k)}
