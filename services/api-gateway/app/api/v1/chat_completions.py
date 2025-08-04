from fastapi import APIRouter, Request, HTTPException
import aiohttp

from config import LLM_SERVICE_URL


chat_completions_router = APIRouter()


@chat_completions_router.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        body = await request.json()
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{LLM_SERVICE_URL}/v1/chat/completions", json=body) as response:
                if response.status != 200:
                    detail = await response.text()
                    raise HTTPException(status_code=response.status, detail=detail)
                return await response.json()
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"LLM service unavailable: {e}")
