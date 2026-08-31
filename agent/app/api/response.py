from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agent import agent_invoke
from app.api.rate_limit import limiter
from app.config import settings
from app.logger import get_logger
from db.engine import get_db
from modules.auth.jwt_service import get_current_user
from modules.chat.dependencies import get_chat_service
from modules.chat.schemas.message import ChatRequest, ChatResponse

logger = get_logger(__name__)
response_router = APIRouter()


@response_router.post("/v1/response", response_model=ChatResponse)
@limiter.limit(f"{settings.NUM_REQUESTS_PER_MINUTE}/minute")
async def create_response_endpoint(
    request: Request,
    body: list[ChatRequest],
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
) -> ChatResponse:
    if not body:
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")

    chat_service = get_chat_service(db)

    # Get or create session
    session_id = body[0].session_id if body else None
    if not session_id:
        first_user_msg = next((m.content for m in body if m.role == "user"), "New chat")
        session = await chat_service.create_session(user_id=user_id, title=first_user_msg[:100])
        session_id = str(session.id)
    else:
        session = await chat_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if str(session.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

    # Save user messages
    for msg in body:
        if msg.role == "user":
            await chat_service.add_message(session_id, msg.role, msg.content)

    # Get history from DB
    history = await chat_service.get_history_for_agent(session_id)
    messages_for_agent = history if len(history) >= len(body) else [m.model_dump() for m in body]

    # Invoke agent
    response = await agent_invoke(messages_for_agent)

    # Save assistant response
    await chat_service.add_message(session_id, response["role"], response["content"])

    return ChatResponse(session_id=session_id, **response)
