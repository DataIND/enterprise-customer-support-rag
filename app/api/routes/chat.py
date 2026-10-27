"""Chat / RAG query and development auth endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, create_access_token, get_current_user
from app.db.session import get_db
from app.schemas import (
    ChatRequest,
    ChatResponse,
    SourceReference,
    TokenRequest,
    TokenResponse,
)
from app.services.rag import RAGService

router = APIRouter()


@router.post("/token", response_model=TokenResponse, tags=["auth"])
async def issue_token(body: TokenRequest) -> TokenResponse:
    """Issue a JWT for local development and testing.

    Replace this endpoint with a production identity provider integration.
    """
    token = create_access_token(
        subject=body.user_id,
        tenant_id=body.tenant_id,
        role=body.role,
    )
    return TokenResponse(
        access_token=token,
        tenant_id=body.tenant_id,
        role=body.role,
    )


@router.post("", response_model=ChatResponse)
async def ask_question(
    body: ChatRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ChatResponse:
    """Retrieve tenant-scoped context and generate a grounded answer."""
    service = RAGService(db)
    result = await service.answer(
        tenant_id=user.tenant_id,
        question=body.question,
    )
    return ChatResponse(
        answer=result.answer,
        abstained=result.abstained,
        sources=[
            SourceReference(
                document_id=s.document_id,
                chunk_id=s.chunk_id,
                filename=s.filename,
                score=s.score,
                excerpt=s.excerpt,
            )
            for s in result.sources
        ],
    )
