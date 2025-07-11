import numpy as np
import json
import hashlib
from valkey.asyncio import Valkey as AsyncValkey




class ValkeySemanticCache:
    """
    Simple semantic cache using Valkey.
    Stores embeddings as JSON and payload as value.
    """

    def __init__(self, host="localhost", port=6380, db=0, cache_prefix="semantic_cache", threshold=0.8):
        self.client = AsyncValkey(host=host, port=port, db=db, decode_responses=True)
        self.prefix = cache_prefix
        self.threshold = threshold

    def _make_key(self, text: str) -> str:
        """
        Generate a hash key from text.
        """
        h = hashlib.md5(text.encode()).hexdigest()
        return f"{self.prefix}:{h}"

    async def set(self, text: str, embedding: np.ndarray, payload: dict):
        """
        Store embedding & payload as JSON.
        """
        key = self._make_key(text)
        data = {
            "embedding": embedding.tolist(),
            "payload": payload
        }
        await self.client.set(key, json.dumps(data))

    async def get(self, query_embedding: np.ndarray) -> dict | None:
        """
        Scan all cache keys, compute similarity, return payload if above threshold.
        """
        keys = await self.client.keys(f"{self.prefix}:*")
        best_score = 0
        best_payload = None

        for key in keys:
            raw = await self.client.get(key)
            if raw:
                obj = json.loads(raw)
                cached_emb = np.array(obj["embedding"])
                score = self._cosine_similarity(query_embedding, cached_emb)
                if score > self.threshold and score > best_score:
                    best_score = score
                    best_payload = obj["payload"]

        return best_payload

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)