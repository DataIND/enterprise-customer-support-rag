"""Document upload and ingestion status endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Role, get_current_user, require_roles
from app.db.session import get_db
from app.schemas import DocumentResponse
from app.services.documents import DocumentService

router = APIRouter()


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AGENT))],
)
async def upload_document(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> DocumentResponse:
    """Upload a knowledge-base document and enqueue ingestion."""
    service = DocumentService(db)
    try:
        document = await service.upload(
            tenant_id=user.tenant_id,
            uploaded_by=user.user_id,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DocumentResponse:
    """Fetch document metadata scoped to the caller's tenant."""
    service = DocumentService(db)
    document = service.get_for_tenant(document_id, user.tenant_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return DocumentResponse.model_validate(document)
