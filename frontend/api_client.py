# frontend/api_client.py
import logging
import requests
from config import API_BASE_URL

logger = logging.getLogger(__name__)
TIMEOUT_SECONDS = 60


def send_message(message: str, session_id: str | None = None) -> dict:
    """Send a message to the agent and return the response."""
    try:
        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id

        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/message",
            json=payload,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to the backend API. Is it running?"}
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        return {"success": False, "error": detail}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_session() -> dict:
    """Create a new conversation session."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/session",
            timeout=10,
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_health() -> bool:
    """Return True if the backend API is reachable."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False