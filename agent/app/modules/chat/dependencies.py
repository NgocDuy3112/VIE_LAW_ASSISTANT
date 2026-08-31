from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import async_session
from modules.chat.repositories.session_repository import SessionRepository
from modules.chat.repositories.message_repository import MessageRepository
from modules.chat.services.chat_service import ChatService


def get_session_repository(db: AsyncSession) -> SessionRepository:
    return SessionRepository(db)


def get_message_repository(db: AsyncSession) -> MessageRepository:
    return MessageRepository(db)


def get_chat_service(db: AsyncSession) -> ChatService:
    return ChatService(
        session_repo=get_session_repository(db),
        message_repo=get_message_repository(db),
    )
