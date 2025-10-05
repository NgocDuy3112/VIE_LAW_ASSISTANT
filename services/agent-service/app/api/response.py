from fastapi import APIRouter, HTTPException, Request, Depends
from uuid import UUID
import asyncio
# from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.message import Message
from app.api.rate_limit import limiter
from app.config import settings
from app.log.logger import get_logger
# from app.db.dependencies import get_postgresql_async_session



logger = get_logger(__name__)
response_router = APIRouter()



@response_router.post("/v1/response", response_model=Message)
@limiter.limit(f"{settings.NUM_REQUESTS_PER_MINUTE}/minute")
async def create_response_endpoint(
    request: Request,
    body: list[Message]
) -> Message:
    """
    Create a chat completion based on chat history and incoming messages.
    """
    if not body:
        logger.info("Empty body received.")
        raise HTTPException(status_code=400, detail="Messages cannot be empty.")
    pass