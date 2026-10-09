from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routers import documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Document Q&A API", lifespan=lifespan)
app.include_router(documents.router)


@app.get("/health")
def health():
    return {"status": "ok"}