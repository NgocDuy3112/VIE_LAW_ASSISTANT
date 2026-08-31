import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatSession
from app.logger import get_logger

logger = get_logger(__name__)


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, title: str | None = None) -> ChatSession:
        session = ChatSession(user_id=uuid.UUID(user_id), title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        logger.info("Created session: id=%s", session.id)
        return session

    async def get_by_id(self, session_id: str) -> ChatSession | None:
        return await self.db.get(ChatSession, uuid.UUID(session_id))

    async def get_by_user(self, user_id: str) -> list[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == uuid.UUID(user_id))
            .order_by(ChatSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, session_id: str) -> bool:
        session = await self.get_by_id(session_id)
        if not session:
            return False
        await self.db.delete(session)
        await self.db.commit()
        logger.info("Deleted session: id=%s", session_id)
        return True
