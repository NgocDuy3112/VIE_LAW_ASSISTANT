import numpy as np
import aiohttp

from app.logger import get_logger
from config import settings

logger = get_logger(__name__)


class EmbeddingService:
    """Calls infinity embedding server via HTTP API."""

    def __init__(self):
        self.base_url = settings.EMBEDDING_URL or "http://infinity-embedding:8010"

    async def embed(self, text: str) -> np.ndarray:
        url = self.base_url.rstrip("/") + "/v1/embeddings"
        payload = {"input": [text], "model": settings.EMBEDDING_MODEL}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                response.raise_for_status()
                data = await response.json()
                return np.array(data["data"][0]["embedding"])

    async def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        url = self.base_url.rstrip("/") + "/v1/embeddings"
        payload = {"input": texts, "model": settings.EMBEDDING_MODEL}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                response.raise_for_status()
                data = await response.json()
                return [np.array(item["embedding"]) for item in data["data"]]
