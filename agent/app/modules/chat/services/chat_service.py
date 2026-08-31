from modules.chat.repositories.session_repository import SessionRepository
from modules.chat.repositories.message_repository import MessageRepository
from db.models import ChatSession, ChatMessage
from app.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    def __init__(self, session_repo: SessionRepository, message_repo: MessageRepository):
        self.session_repo = session_repo
        self.message_repo = message_repo

    async def create_session(self, user_id: str, title: str | None = None) -> ChatSession:
        return await self.session_repo.create(user_id, title)

    async def get_session(self, session_id: str) -> ChatSession | None:
        return await self.session_repo.get_by_id(session_id)

    async def get_sessions_by_user(self, user_id: str) -> list[ChatSession]:
        return await self.session_repo.get_by_user(user_id)

    async def delete_session(self, session_id: str) -> bool:
        return await self.session_repo.delete(session_id)

    async def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        return await self.message_repo.create(session_id, role, content)

    async def get_messages(self, session_id: str) -> list[ChatMessage]:
        return await self.message_repo.get_by_session(session_id)

    async def get_history_for_agent(self, session_id: str) -> list[dict]:
        messages = await self.get_messages(session_id)
        return [{"role": m.role, "content": m.content} for m in messages]
