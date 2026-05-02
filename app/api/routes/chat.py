# app/api/routes/chat.py
import logging
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import MessageRequest, MessageResponse, SessionResponse
from app.services.chat_service import process_message, start_new_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/message",
    response_model=MessageResponse,
    summary="Send a message to the support agent",
)
async def send_message(request: MessageRequest):
    """
    Send a message to the AI support agent.
    Include session_id to continue an existing conversation.
    Omit session_id to start a new conversation — a new session_id
    will be returned for use in subsequent messages.
    """
    try:
        result = process_message(
            message=request.message,
            session_id=request.session_id,
        )
        return MessageResponse(
            response=result["response"],
            session_id=result["session_id"],
            tools_used=result["tools_used"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again.",
        )


@router.post(
    "/session",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new conversation session",
)
async def create_session():
    """Generate a new session ID for a fresh conversation."""
    session_id = start_new_session()
    return SessionResponse(session_id=session_id)