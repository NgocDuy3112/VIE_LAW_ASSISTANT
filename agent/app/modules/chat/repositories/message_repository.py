import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatMessage
from app.logger import get_logger

logger = get_logger(__name__)


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session_id: str, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=uuid.UUID(session_id), role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_by_session(self, session_id: str) -> list[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == uuid.UUID(session_id))
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())
