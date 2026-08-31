import asyncio
from elasticsearch import AsyncElasticsearch
from config import settings
from app.logger import get_logger

logger = get_logger(__name__)


async def init_elasticsearch_index() -> None:
    client = AsyncElasticsearch(settings.ELASTICSEARCH_URL)
    try:
        # Retry until Elasticsearch is ready
        for attempt in range(10):
            try:
                if await client.ping():
                    break
            except Exception:
                logger.info("Waiting for Elasticsearch... (attempt %d/10)", attempt + 1)
                await asyncio.sleep(3)
        else:
            logger.error("Elasticsearch not available after 10 attempts")
            return

        if not await client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
            await client.indices.create(
                index=settings.ELASTICSEARCH_INDEX,
                mappings={"properties": {
                    "content": {"type": "text"},
                    "content_hash": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "content_vector": {"type": "dense_vector", "dims": settings.EMBEDDING_DIMENSION, "index": True, "similarity": "cosine"},
                }},
            )
            logger.info("Created Elasticsearch index '%s'", settings.ELASTICSEARCH_INDEX)
    finally:
        await client.close()
