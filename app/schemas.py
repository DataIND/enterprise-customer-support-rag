"""Pydantic request/response schemas."""

from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.core.security import Role


class TokenRequest(BaseModel):
    """Dev-oriented token issuance request."""

    user_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: UUID = Field(default_factory=uuid4)
    role: Role = Role.AGENT


class TokenResponse(BaseModel):
    """Issued access token."""

    access_token: str
    token_type: str = "bearer"
    tenant_id: UUID
    role: Role


class DocumentResponse(BaseModel):
    """Document metadata returned to clients."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: str
    tenant_id: UUID


class ChatRequest(BaseModel):
    """Customer support question."""

    question: str = Field(..., min_length=1, max_length=4000)


class SourceReference(BaseModel):
    """Citation for a retrieved chunk."""

    document_id: UUID
    chunk_id: UUID
    filename: str
    score: float
    excerpt: str


class ChatResponse(BaseModel):
    """Grounded answer with source references."""

    answer: str
    abstained: bool
    sources: list[SourceReference]


class HealthResponse(BaseModel):
    """Liveness probe payload."""

    status: str
