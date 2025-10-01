import asyncio
import re

from langchain_ollama import ChatOllama

from fastapi import HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.message import Message
# from app.schemas.chat_history import ChatHistoryRequest
# from app.core.chat_history import ChatHistoryRepository
from app.config import settings




async def create_response(
    messages: list[Message],
    model: str=settings.MODEL_NAME
) -> Message:
    """
    Generates a chat completion based on chat history + current messages,
    and saves the last exchange to the chat history table.
    """
    if not messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")

    try:
        response = await client.responses.create(
            model=model,
            input=messages
        )
        role = response.output["role"]
        content = response.output["content"]
        content_cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")
    return Message(
        role=role,
        content=content
    )