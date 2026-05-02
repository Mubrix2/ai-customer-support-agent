# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import create_app

client = TestClient(create_app())


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data


def test_create_session():
    response = client.post("/api/v1/chat/session")
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


@patch("app.api.routes.chat.process_message")
def test_send_message_success(mock_process):
    mock_process.return_value = {
        "response": "Hello! How can I help you today?",
        "session_id": "test-session-123",
        "tools_used": [],
    }
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello! How can I help you today?"
    assert data["session_id"] == "test-session-123"
    assert data["tools_used"] == []


@patch("app.api.routes.chat.process_message")
def test_send_message_with_tool_use(mock_process):
    mock_process.return_value = {
        "response": "Your order ORD-001 has been delivered.",
        "session_id": "test-session-123",
        "tools_used": ["check_order_status"],
    }
    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "What is the status of ORD-001?",
            "session_id": "test-session-123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "check_order_status" in data["tools_used"]


def test_send_empty_message():
    response = client.post(
        "/api/v1/chat/message",
        json={"message": ""},
    )
    assert response.status_code == 422


def test_session_continuity():
    """Two requests with same session_id should be accepted."""
    response1 = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello"}
    )
    # Just verify the endpoint accepts a session_id on second call
    session_id = response1.json().get("session_id", "test-id")
    response2 = client.post(
        "/api/v1/chat/message",
        json={"message": "Thanks", "session_id": session_id}
    )
    assert response2.status_code == 200