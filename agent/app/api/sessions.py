from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import get_db
from modules.auth.jwt_service import get_current_user
from modules.chat.dependencies import get_chat_service
from modules.chat.schemas.session import SessionResponse
from modules.chat.schemas.message import MessageResponse

sessions_router = APIRouter(prefix="/v1/sessions", tags=["Sessions"])


@sessions_router.get("", response_model=list[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    chat_service = get_chat_service(db)
    sessions = await chat_service.get_sessions_by_user(user_id=user_id)
    return [
        SessionResponse(id=str(s.id), title=s.title, created_at=s.created_at.isoformat())
        for s in sessions
    ]


@sessions_router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    chat_service = get_chat_service(db)
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    messages = await chat_service.get_messages(session_id)
    return [
        MessageResponse(id=str(m.id), role=m.role, content=m.content, created_at=m.created_at.isoformat())
        for m in messages
    ]


@sessions_router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    chat_service = get_chat_service(db)
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if str(session.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    await chat_service.delete_session(session_id)
    return {"status": "deleted"}
