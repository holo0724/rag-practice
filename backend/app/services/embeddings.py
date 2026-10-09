import httpx

from app.config import settings

BATCH_SIZE = 16


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector per input text."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = httpx.post(
            f"{settings.ollama_base_url}/api/embed",
            json={"model": settings.embed_model, "input": batch},
            timeout=120,
        )
        response.raise_for_status()
        vectors.extend(response.json()["embeddings"])
    return vectors