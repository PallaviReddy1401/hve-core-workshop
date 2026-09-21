"""API behavior tests."""

from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from smartassist.api.app import create_app
from smartassist.core.config import Settings


def test_create_and_continue_conversation() -> None:
    client = TestClient(create_app(Settings()))

    created = client.post(
        "/api/v1/conversations",
        json={"data_classification": "synthetic"},
    )
    assert created.status_code == 201
    created_body = created.json()
    UUID(created_body["conversation_id"], version=4)
    UUID(created_body["correlation_id"], version=4)
    assert created_body["state"] == "active"

    response = client.post(
        f"/api/v1/conversations/{created_body['conversation_id']}/messages",
        headers={"Idempotency-Key": "request-1"},
        json={"content": "Hello"},
    )
    assert response.status_code == 200
    assert response.json()["disposition"] == "answered"
    assert response.json()["category"] == "general"


def test_idempotent_retry_reuses_response() -> None:
    client = TestClient(create_app(Settings()))
    conversation_id = client.post(
        "/api/v1/conversations",
        json={"data_classification": "deidentified"},
    ).json()["conversation_id"]
    path = f"/api/v1/conversations/{conversation_id}/messages"
    headers = {"Idempotency-Key": "same-request"}

    first = client.post(path, headers=headers, json={"content": "Retry me"})
    second = client.post(path, headers=headers, json={"content": "Retry me"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_idempotency_conflict_is_explicit() -> None:
    client = TestClient(create_app(Settings()))
    conversation_id = client.post(
        "/api/v1/conversations",
        json={"data_classification": "synthetic"},
    ).json()["conversation_id"]
    path = f"/api/v1/conversations/{conversation_id}/messages"
    headers = {"Idempotency-Key": "reused-key"}
    client.post(path, headers=headers, json={"content": "First"})

    response = client.post(path, headers=headers, json={"content": "Different"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "idempotency_conflict"


def test_missing_conversation_is_explicit() -> None:
    client = TestClient(create_app(Settings()))

    response = client.post(
        "/api/v1/conversations/00000000-0000-4000-8000-000000000001/messages",
        json={"content": "Hello"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "conversation_not_found"


def test_production_classification_is_rejected() -> None:
    client = TestClient(create_app(Settings()))

    response = client.post(
        "/api/v1/conversations",
        json={"data_classification": "production"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_configured_message_limit_is_enforced() -> None:
    client = TestClient(create_app(Settings(max_message_length=5)))
    conversation_id = client.post(
        "/api/v1/conversations",
        json={"data_classification": "synthetic"},
    ).json()["conversation_id"]

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "Too long"},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "message_too_large"
