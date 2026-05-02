# app/api/schemas.py
from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="The user's message to the support agent",
        examples=["What is the status of my order ORD-001?"]
    )
    session_id: str | None = Field(
        default=None,
        description="Session ID for continuing an existing conversation. "
                    "Leave empty to start a new conversation."
    )


class MessageResponse(BaseModel):
    response: str = Field(description="The agent's response")
    session_id: str = Field(description="Session ID — use this for follow-up messages")
    tools_used: list[str] = Field(
        default=[],
        description="Names of tools the agent called to generate this response"
    )


class SessionResponse(BaseModel):
    session_id: str
    message: str = "New session created. Send your first message."


class HealthResponse(BaseModel):
    status: str
    env: str
    database: str