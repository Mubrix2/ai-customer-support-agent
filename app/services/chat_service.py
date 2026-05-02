# app/services/chat_service.py
import logging
import uuid

from app.core.agent import chat

logger = logging.getLogger(__name__)


def process_message(message: str, session_id: str | None = None) -> dict:
    """
    Process a user message through the agent.
    Generates a session_id if one is not provided.

    Args:
        message: The user's message
        session_id: Existing session ID for continuing a conversation,
                   or None to start a new one

    Returns:
        Dict with response, session_id, and tools_used
    """
    if not message.strip():
        raise ValueError("Message cannot be empty")

    # Generate session ID for new conversations
    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"New conversation started. session_id={session_id}")

    result = chat(message=message, session_id=session_id)
    return result


def start_new_session() -> str:
    """Generate a fresh session ID for a new conversation."""
    session_id = str(uuid.uuid4())
    logger.info(f"New session created: {session_id}")
    return session_id