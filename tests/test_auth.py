"""Auth token issuance tests."""

from fastapi.testclient import TestClient


def test_issue_token(client: TestClient) -> None:
    response = client.post("/api/v1/chat/token", json={"role": "agent"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["role"] == "agent"
