from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.chat_history import ChatHistoryRepository
from app.schemas.chat_history import *
from app.db.dependencies import get_postgresql_async_session


router = APIRouter("/chat-history", tags=["Chat History"])


@router.post("/", status_code=201)
async def create_chat_history_endpoint(request: ChatHistoryRequest, db: AsyncSession = Depends(get_postgresql_async_session)):
    repo = ChatHistoryRepository(db)
    await repo.create(request)
    return {"message": "Chat history created successfully"}



@router.get("/", response_model=list[ChatHistoryResponse])
async def get_chat_history_endpoint(
    user_id: UUID | None = None, 
    session_id: UUID | None = None, 
    db: AsyncSession = Depends(get_postgresql_async_session)
):
    repo = ChatHistoryRepository(db)
    return await repo.get_chat_history(user_id, session_id)



@router.delete("/", status_code=204)
async def delete_chat_history_endpoint(
    user_id: UUID | None = None, 
    session_id: UUID | None = None, 
    db: AsyncSession = Depends(get_postgresql_async_session)
):
    repo = ChatHistoryRepository(db)
    deleted_count = await repo.delete_chat_history(user_id, session_id)
    return {"message": "Chat history deleted successfully"}