from elasticsearch import AsyncElasticsearch

from app.logger import get_logger
from config import settings

logger = get_logger(__name__)


class DocumentRepository:
    """Handles all Elasticsearch operations for documents."""

    def __init__(self, client: AsyncElasticsearch):
        self.client = client
        self.index = settings.ELASTICSEARCH_INDEX

    async def search_lexical(self, query: str, size: int = 10, filters: dict | None = None) -> list[dict]:
        must = [{"match": {"content": query}}]
        if filters:
            must.append(filters)
        result = await self.client.search(index=self.index, size=size, query={"bool": {"must": must}})
        return result["hits"]["hits"]

    async def search_semantic(self, query_vector: list[float], size: int = 10) -> list[dict]:
        result = await self.client.search(
            index=self.index,
            size=size,
            knn={"field": "content_vector", "query_vector": query_vector, "k": size, "num_candidates": max(50, size * 5)},
        )
        return result["hits"]["hits"]

    async def count_by_hash(self, content_hash: str) -> int:
        result = await self.client.count(index=self.index, query={"term": {"content_hash": content_hash}})
        return result["count"]

    async def index_document(self, document_id: str, source: dict) -> None:
        await self.client.index(index=self.index, id=document_id, document=source, refresh="wait_for")

    async def index_exists(self) -> bool:
        return await self.client.indices.exists(index=self.index)

    async def create_index(self, mappings: dict) -> None:
        await self.client.indices.create(index=self.index, mappings=mappings)
