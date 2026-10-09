from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class Chunk:
    content: str
    page: int
    position: int  # order of the chunk within the document


def extract_pages(path: Path) -> list[tuple[int, str]]:
    """Return a list of (page_number, text) for a PDF or text file."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return [
            (i + 1, page.extract_text() or "")
            for i, page in enumerate(reader.pages)
        ]
    if suffix in {".txt", ".md"}:
        return [(1, path.read_text(encoding="utf-8", errors="ignore"))]
    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_pages(
    pages: list[tuple[int, str]],
    chunk_words: int = 350,
    overlap_words: int = 50,
) -> list[Chunk]:
    """Split each page into overlapping chunks of roughly chunk_words words."""
    if overlap_words >= chunk_words:
        raise ValueError("overlap_words must be smaller than chunk_words")

    step = chunk_words - overlap_words
    chunks: list[Chunk] = []
    position = 0

    for page_number, text in pages:
        words = text.split()
        for start in range(0, len(words), step):
            piece = words[start : start + chunk_words]
            if not piece:
                break
            chunks.append(Chunk(" ".join(piece), page_number, position))
            position += 1
            if start + chunk_words >= len(words):
                break

    return chunks


if __name__ == "__main__":
    import sys

    file_path = Path(sys.argv[1])
    result = chunk_pages(extract_pages(file_path))
    print(f"{len(result)} chunks")
    for c in result[:5]:
        print(f"\n--- chunk {c.position} (page {c.page}, {len(c.content.split())} words) ---")
        print(c.content)