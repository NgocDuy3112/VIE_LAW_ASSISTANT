import asyncio
import re
from openai import AsyncOpenAI

from fastapi import HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.message import Message
# from app.schemas.chat_history import ChatHistoryRequest
# from app.core.chat_history import ChatHistoryRepository
from app.config import REQUEST_TIMEOUT_SECONDS, OPENAI_API_KEY, BASE_URL, MODEL_NAME


client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL, timeout=REQUEST_TIMEOUT_SECONDS)


async def create_chat_completion(
    messages: list[Message],
    model: str=MODEL_NAME
) -> Message:
    """
    Generates a chat completion based on chat history + current messages,
    and saves the last exchange to the chat history table.
    """
    if not messages:
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")

    # Step 4: Generate response from LLM
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
        message_data = response.choices[0].message
        role = message_data.role
        content = message_data.content
        content_cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")
    return Message(
        role=role,
        content=[
            {
                "type": "text",
                "text": content_cleaned
            }
        ]
    )