import asyncio
from fastapi import APIRouter, HTTPException, Request

from app.core.chat_completions import create_chat_completion
from app.schemas.message import Message
from app.api.rate_limit import limiter
from app.config import NUM_REQUESTS_PER_MINUTE, REQUEST_TIMEOUT_SECONDS
from app.log.logger import get_logger


logger = get_logger(__name__)
chat_completions_router = APIRouter()


@chat_completions_router.post("/v1/chat/completions", response_model=Message)
@limiter.limit(f"{NUM_REQUESTS_PER_MINUTE}/minute")
async def create_chat_completion_endpoint(request: Request, body: list[Message]) -> Message:
    """
    Create a chat completion based on the provided messages.
    """
    if not body:
        logger.info()
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")
    try:
        response = await asyncio.wait_for(
            create_chat_completion(body),
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        return response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")