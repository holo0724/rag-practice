from fastapi import FastAPI

app = FastAPI(title="Document Q&A API")

@app.get("/health")
def health():
    return {"status": "ok"}