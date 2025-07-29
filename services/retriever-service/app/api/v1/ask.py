import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from qdrant_client import AsyncQdrantClient

from app.helpers.caching import ValkeySemanticCache
from app.schemas.ask import AskRequest, AskResponse
from app.core.v1.ask import create_ask_service
from app.dependencies import get_async_qdrant_client, get_valkey_cache
from app.api.rate_limit import limiter
from app.config import NUM_REQUESTS_PER_MINUTE, REQUEST_TIMEOUT_SECONDS
from app.log.logger import get_logger


logger = get_logger(__name__)
ask_router = APIRouter(prefix="/v1/ask")



@ask_router.post("/", response_model=AskResponse)
@limiter.limit(f"{NUM_REQUESTS_PER_MINUTE}/minute")
async def ask(
    request: Request,
    body: AskRequest,
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client),
    valkey_cache: ValkeySemanticCache = Depends(get_valkey_cache)
) -> AskResponse:
    """
    Retrieve legal answers based on question and context from Qdrant.
    """
    if not body.question or not body.question.strip():
        logger.info("AskRequest 'question' is empty.")
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        response = await asyncio.wait_for(
            create_ask_service(body, async_qdrant_client, valkey_cache),
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        return response
    except asyncio.TimeoutError:
        logger.warning("Request timed out after %s seconds", REQUEST_TIMEOUT_SECONDS)
        raise HTTPException(status_code=504, detail="Request timed out. Please try again later.")