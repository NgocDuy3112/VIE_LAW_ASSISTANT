from fastapi import APIRouter, HTTPException, Request, Depends
from uuid import UUID
import asyncio
# from sqlalchemy.ext.asyncio import AsyncSession

from app.core.chat_completions import create_chat_completion
from app.schemas.message import Message
from app.api.rate_limit import limiter
from app.config import NUM_REQUESTS_PER_MINUTE, REQUEST_TIMEOUT_SECONDS
from app.log.logger import get_logger
# from app.db.dependencies import get_postgresql_async_session



logger = get_logger(__name__)
chat_completions_router = APIRouter()



@chat_completions_router.post("/v1/chat/completions", response_model=Message)
@limiter.limit(f"{NUM_REQUESTS_PER_MINUTE}/minute")
async def create_chat_completion_endpoint(
    request: Request,
    body: list[Message]
) -> Message:
    """
    Create a chat completion based on chat history and incoming messages.
    """
    if not body:
        logger.info("Empty body received.")
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")

    try:
        # Call the core chat completion logic, which handles history and saving
        response = await asyncio.wait_for(
            create_chat_completion(messages=body),
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        return response
    except asyncio.TimeoutError:
        logger.error("Chat completion request timed out.")
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")