"""Chunking unit tests."""

from app.rag.chunking import chunk_text


def test_chunk_text_empty() -> None:
    assert chunk_text("") == []


def test_chunk_text_overlap() -> None:
    text = "a" * 50
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) >= 2
    assert all(len(c) <= 20 for c in chunks)


def test_chunk_text_invalid_overlap() -> None:
    try:
        chunk_text("hello", chunk_size=10, overlap=10)
        raised = False
    except ValueError:
        raised = True
    assert raised
