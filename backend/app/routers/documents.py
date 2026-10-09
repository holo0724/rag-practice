import tempfile
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Chunk as ChunkRow
from app.models import Document
from app.services.embeddings import embed_texts
from app.services.ingestion import chunk_pages, extract_pages

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_SUFFIXES = {".pdf", ".txt", ".md"}


@router.post("", status_code=201)
def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(415, "Only PDF, TXT, and MD files are supported.")

    data = file.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File is too large (10 MB maximum).")

    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(data)
        tmp.flush()
        try:
            pages = extract_pages(Path(tmp.name))
        except Exception:
            raise HTTPException(422, "Could not read this file.")

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(422, "No readable text found in this file.")

    try:
        vectors = embed_texts([c.content for c in chunks])
    except httpx.HTTPError:
        raise HTTPException(503, "Embedding service is unavailable.")

    document = Document(
        filename=file.filename,
        chunks=[
            ChunkRow(
                content=c.content,
                page=c.page,
                position=c.position,
                embedding=vector,
            )
            for c, vector in zip(chunks, vectors)
        ],
    )
    db.add(document)
    db.commit()

    return {"id": document.id, "filename": document.filename, "chunks": len(chunks)}