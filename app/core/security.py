"""JWT authentication and RBAC helpers (reference implementation)."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class Role(StrEnum):
    """Application roles."""

    ADMIN = "admin"
    AGENT = "agent"
    VIEWER = "viewer"


class TokenPayload(BaseModel):
    """Decoded JWT claims."""

    sub: str
    tenant_id: UUID
    role: Role
    exp: int | None = None


class CurrentUser(BaseModel):
    """Authenticated principal attached to requests."""

    user_id: str
    tenant_id: UUID
    role: Role


def create_access_token(
    *,
    subject: str,
    tenant_id: UUID,
    role: Role,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.now(UTC) + (
        expires_delta
        or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "tenant_id": str(tenant_id),
        "role": role.value,
        "exp": expire,
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload.model_validate(payload)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
) -> CurrentUser:
    """Extract the current user from the Authorization header."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token_data = decode_access_token(credentials.credentials)
    return CurrentUser(
        user_id=token_data.sub,
        tenant_id=token_data.tenant_id,
        role=token_data.role,
    )


def require_roles(*allowed: Role):
    """Dependency factory enforcing role-based access control."""

    async def _checker(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _checker
