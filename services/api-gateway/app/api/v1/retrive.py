from fastapi import APIRouter, Request, HTTPException
import aiohttp
from app.config import DOCUMENT_SERVICE_URL


retrieve_router = APIRouter()


@retrieve_router.post("/v1/retrieve")
async def retrieve_docs(request: Request):
    body = await request.json()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{DOCUMENT_SERVICE_URL}/v1/retrieve", json=body) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=resp.status, detail=await resp.text())
                return await resp.json()
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Retriever service error: {e}")