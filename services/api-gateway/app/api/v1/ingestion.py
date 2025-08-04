from fastapi import APIRouter, UploadFile, File, HTTPException
import aiohttp
from app.config import DOCUMENT_SERVICE_URL


ingestion_router = APIRouter()


@ingestion_router.post("/v1/ingestion/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    try:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("file", await file.read(), filename=file.filename, content_type=file.content_type)

            async with session.post(f"{DOCUMENT_SERVICE_URL}/v1/ingestion/pdf", data=form) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=resp.status, detail=await resp.text())
                return await resp.json()
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=f"Ingestion error: {e}")