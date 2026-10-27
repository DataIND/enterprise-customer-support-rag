"""Document upload and metadata management."""

import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Document, DocumentStatus, Tenant
from app.tasks.ingestion import ingest_document


class DocumentService:
    """Handles document metadata and ingestion scheduling."""

    def __init__(self, db: Session, *, upload_dir: str = "/tmp/rag_uploads") -> None:
        self.db = db
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_tenant(self, tenant_id: UUID) -> None:
        tenant = self.db.get(Tenant, tenant_id)
        if tenant is None:
            self.db.add(Tenant(id=tenant_id, name=f"tenant-{tenant_id}"))
            self.db.flush()

    def _validate_file(self, file: UploadFile, size: int) -> None:
        allowed = {
            ext.strip().lower()
            for ext in settings.ALLOWED_UPLOAD_EXTENSIONS.split(",")
            if ext.strip()
        }
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in allowed:
            raise ValueError(f"Unsupported file type: {suffix or '(none)'}")
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size > max_bytes:
            raise ValueError(
                f"File exceeds max size of {settings.MAX_UPLOAD_SIZE_MB} MB"
            )

    async def upload(
        self,
        *,
        tenant_id: UUID,
        uploaded_by: str,
        file: UploadFile,
    ) -> Document:
        """Persist upload metadata and enqueue background ingestion."""
        content = await file.read()
        self._validate_file(file, len(content))
        self._ensure_tenant(tenant_id)

        document_id = uuid.uuid4()
        filename = file.filename or f"{document_id}.bin"
        storage_path = self.upload_dir / str(tenant_id) / f"{document_id}_{filename}"
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)

        document = Document(
            id=document_id,
            tenant_id=tenant_id,
            filename=filename,
            content_type=file.content_type,
            storage_path=str(storage_path),
            status=DocumentStatus.PENDING,
            uploaded_by=uploaded_by,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        ingest_document.delay(str(document.id))
        return document

    def get_for_tenant(self, document_id: UUID, tenant_id: UUID) -> Document | None:
        """Fetch a document limited to the caller's tenant."""
        document = self.db.get(Document, document_id)
        if document is None or document.tenant_id != tenant_id:
            return None
        return document
