"""JWT helper tests."""

from uuid import uuid4

from app.core.security import Role, create_access_token, decode_access_token


def test_create_and_decode_token() -> None:
    tenant_id = uuid4()
    token = create_access_token(
        subject="user-1",
        tenant_id=tenant_id,
        role=Role.ADMIN,
    )
    payload = decode_access_token(token)
    assert payload.sub == "user-1"
    assert payload.tenant_id == tenant_id
    assert payload.role == Role.ADMIN
