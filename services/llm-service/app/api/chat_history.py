from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.chat_history import ChatHistoryRepository
from app.schemas.chat_history import ChatHistoryRequest, ChatHistoryResponse
from app.db.dependencies import get_postgresql_async_session
from app.auth import get_current_user


chat_history_router = APIRouter(
    prefix="/chat-history",
    tags=["Chat History"],
    responses={404: {"description": "Not found"}},
)


@chat_history_router.post("/", response_model=ChatHistoryResponse, status_code=201)
async def create_chat_history(
    request: ChatHistoryRequest,
    session: AsyncSession = Depends(get_postgresql_async_session),
    current_user_id: UUID = Depends(get_current_user),
):
    repo = ChatHistoryRepository(session)

    # Replace user_id from request with current_user_id for safety
    request.user_id = current_user_id
    request.timestamp = request.timestamp or datetime.utcnow()

    return await repo.create(request)


@chat_history_router.get("/", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    session_id: UUID | None = None,
    session: AsyncSession = Depends(get_postgresql_async_session),
    current_user_id: UUID = Depends(get_current_user),
):
    repo = ChatHistoryRepository(session)
    return await repo.get_chat_history(user_id=current_user_id, session_id=session_id)


@chat_history_router.delete("/", status_code=204)
async def delete_chat_history(
    session_id: UUID | None = None,
    session: AsyncSession = Depends(get_postgresql_async_session),
    current_user_id: UUID = Depends(get_current_user),
):
    repo = ChatHistoryRepository(session)
    await repo.delete_chat_history(user_id=current_user_id, session_id=session_id)
    return None