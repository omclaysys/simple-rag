from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from app.rag import ingest, search, ask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def issupported(filename: str) -> bool:
    name = filename.lower()
    return name.endswith(".pdf") or name.endswith(".docx")


@app.post("/upload")
async def upload(file: Annotated[UploadFile, File()]):
    if not file.filename or not issupported(file.filename):
        raise HTTPException(400, "Only PDF and DOCX supported")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 20MB)")

    try:
        count = ingest(file.filename, data)
    except Exception as error:
        raise HTTPException(400, str(error))

    if count == 0:
        raise HTTPException(400, "No text found in document")

    return {"filename": file.filename, "chunksadded": count}


@app.get("/retrieve")
async def retrieve(query: Annotated[str, Query(min_length=1)], topk: int = 3):
    return {
        "query": query,
        "topk": topk,
        "results": search(query, topk),
    }


@app.post("/ask")
async def askquestion(payload: dict):
    question = payload.get("question") if isinstance(payload, dict) else None
    if not question or not str(question).strip():
        raise HTTPException(400, "question is required")

    try:
        return ask(str(question))
    except Exception as error:
        raise HTTPException(500, str(error))
