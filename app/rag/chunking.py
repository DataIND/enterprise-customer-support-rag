"""Text chunking utilities."""

from app.core.config import settings


def chunk_text(
    text: str,
    *,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping character-based chunks.

    Replace with a token-aware splitter for production workloads.
    """
    size = chunk_size or settings.CHUNK_SIZE
    ov = overlap if overlap is not None else settings.CHUNK_OVERLAP
    if size <= 0:
        raise ValueError("chunk_size must be positive")
    if ov < 0 or ov >= size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    length = len(normalized)
    while start < length:
        end = min(start + size, length)
        chunks.append(normalized[start:end])
        if end == length:
            break
        start = end - ov
    return chunks
