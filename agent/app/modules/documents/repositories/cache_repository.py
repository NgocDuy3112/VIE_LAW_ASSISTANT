import json
import hashlib

import numpy as np
from redis.asyncio import Redis

from app.logger import get_logger
from config import settings

logger = get_logger(__name__)


class CacheRepository:
    """Handles Redis cache operations for semantic search."""

    def __init__(self, client: Redis, prefix: str = "semantic_cache", threshold: float = 0.8):
        self.client = client
        self.prefix = prefix
        self.threshold = threshold

    def _make_key(self, text: str) -> str:
        h = hashlib.md5(text.encode()).hexdigest()
        return f"{self.prefix}:{h}"

    async def set(self, text: str, embedding: np.ndarray, payload: dict) -> None:
        key = self._make_key(text)
        data = {"embedding": embedding.tolist(), "payload": payload}
        await self.client.set(key, json.dumps(data))

    async def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[dict]:
        keys = await self.client.keys(f"{self.prefix}:*")
        scored_results = []
        for key in keys:
            raw = await self.client.get(key)
            if raw:
                obj = json.loads(raw)
                cached_emb = np.array(obj["embedding"])
                score = self._cosine_similarity(query_embedding, cached_emb)
                if score > self.threshold:
                    scored_results.append({"score": score, "payload": obj["payload"]})
        return sorted(scored_results, key=lambda x: x["score"], reverse=True)[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))
