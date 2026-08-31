from pydantic import BaseModel

from app.schemas.message import Message


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class ChatRequest(Message):
    session_id: str | None = None


class ChatResponse(Message):
    session_id: str | None = None
