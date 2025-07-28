import asyncio
from uuid import UUID
from datetime import datetime
from openai import AsyncOpenAI

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.message import Message
from app.schemas.chat_history import ChatHistoryRequest
from app.core.chat_history import ChatHistoryRepository
from app.config import REQUEST_TIMEOUT_SECONDS, OPENAI_API_KEY, BASE_URL, MODEL_NAME


client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS)


async def create_chat_completion(
    messages: list[Message],
    user_id: UUID,
    db: AsyncSession,
    session_id: UUID | None = None,
    max_history: int = 3,
    model: str=MODEL_NAME
) -> Message:
    """
    Generates a chat completion based on chat history + current messages,
    and saves the last exchange to the chat history table.
    """
    if not messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")

    repo = ChatHistoryRepository(db)

    # Step 1: Fetch recent history
    history = await repo.get_chat_history(user_id=user_id, limit=max_history)

    # Step 2: Convert to list[Message]
    history_msgs: list[Message] = []
    for h in reversed(history):  # maintain chronological order
        history_msgs.append(Message(role="user", content=[{"type": "text", "text": h.question}]).model_dump())
        history_msgs.append(Message(role="assistant", content=[{"type": "text", "text": h.answer}]).model_dump())

    # Step 3: Combine with current
    all_msgs = history_msgs + messages

    # Step 4: Generate response from LLM
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=all_msgs
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")

    # Step 5: Save last user message + model reply
    last_user_msg = next((m for m in reversed(messages) if m.role == "user"), None)
    if last_user_msg:
        question_text = last_user_msg.content[0]["text"] if last_user_msg.content else ""
        answer_text = response.content[0]["text"] if response.content else ""
        await repo.add_history(ChatHistoryRequest(
            user_id=user_id,
            session_id=session_id,
            question=question_text,
            answer=answer_text,
        ))

    return response