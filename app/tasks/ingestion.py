"""Asynchronous document ingestion: parse, chunk, embed, store."""

import asyncio
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete

from app.db.models import Document, DocumentChunk, DocumentStatus
from app.db.session import SessionLocal
from app.rag.chunking import chunk_text
from app.rag.providers import get_embedding_provider
from app.tasks.celery_app import celery_app


def _read_text(path: Path) -> str:
    """Best-effort text extraction for supported upload types."""
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        # Placeholder: integrate a PDF parser (e.g. pypdf) for production.
        raise ValueError("PDF parsing is not yet implemented")
    raise ValueError(f"Unsupported file type for ingestion: {suffix}")


async def _embed_chunks(chunks: list[str]) -> list[list[float]]:
    provider = get_embedding_provider()
    return await provider.embed(chunks)


@celery_app.task(name="ingest_document", bind=True, max_retries=3)
def ingest_document(self, document_id: str) -> dict:
    """Parse, chunk, embed, and persist a document within its tenant scope."""
    db = SessionLocal()
    try:
        document = db.get(Document, UUID(document_id))
        if document is None:
            return {"status": "missing", "document_id": document_id}

        document.status = DocumentStatus.PROCESSING
        document.error_message = None
        db.commit()

        text = _read_text(Path(document.storage_path))
        chunks = chunk_text(text)
        if not chunks:
            document.status = DocumentStatus.FAILED
            document.error_message = "No extractable text"
            db.commit()
            return {"status": "failed", "reason": "empty"}

        embeddings = asyncio.run(_embed_chunks(chunks))

        # Replace prior chunks for idempotent re-ingestion.
        db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document.id)
        )

        for index, (content, embedding) in enumerate(zip(chunks, embeddings, strict=True)):
            db.add(
                DocumentChunk(
                    tenant_id=document.tenant_id,
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    embedding=embedding,
                )
            )

        document.status = DocumentStatus.READY
        db.commit()
        return {
            "status": "ready",
            "document_id": document_id,
            "chunks": len(chunks),
        }
    except Exception as exc:  # noqa: BLE001 - surface failure on document record
        db.rollback()
        document = db.get(Document, UUID(document_id))
        if document is not None:
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)
            db.commit()
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()
