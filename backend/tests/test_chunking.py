import pytest

from app.services.ingestion import chunk_pages


def test_chunks_respect_size_and_overlap():
    text = " ".join(f"w{i}" for i in range(1000))
    chunks = chunk_pages([(1, text)], chunk_words=100, overlap_words=20)

    assert all(len(c.content.split()) <= 100 for c in chunks)
    # the start of each chunk repeats the end of the previous one
    assert chunks[1].content.split()[:20] == chunks[0].content.split()[-20:]


def test_positions_are_sequential_and_pages_are_kept():
    pages = [(1, "a " * 150), (2, "b " * 150)]
    chunks = chunk_pages(pages, chunk_words=100, overlap_words=10)

    assert [c.position for c in chunks] == list(range(len(chunks)))
    assert {c.page for c in chunks} == {1, 2}


def test_empty_pages_produce_no_chunks():
    assert chunk_pages([(1, ""), (2, "   ")]) == []


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_pages([(1, "hello world")], chunk_words=10, overlap_words=10)