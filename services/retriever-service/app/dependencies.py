from qdrant_client import AsyncQdrantClient
from app.helpers.caching import ValkeySemanticCache
from functools import lru_cache

from config import QDRANT_CLIENT_URL



@lru_cache()  # so it's only created once
def get_async_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(url=QDRANT_CLIENT_URL)


@lru_cache()
def get_valkey_cache() -> ValkeySemanticCache:
    return ValkeySemanticCache()