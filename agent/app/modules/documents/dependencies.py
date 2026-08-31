from functools import lru_cache
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from modules.documents.repositories.document_repository import DocumentRepository
from modules.documents.repositories.cache_repository import CacheRepository
from modules.documents.services.embedding_service import EmbeddingService
from modules.documents.services.retrieval_service import RetrievalService
from config import settings


@lru_cache()
def get_elasticsearch_client() -> AsyncElasticsearch:
    return AsyncElasticsearch(settings.ELASTICSEARCH_URL)


@lru_cache()
def get_redis_client() -> Redis:
    return Redis.from_url(settings.SEMANTIC_CACHE_REDIS_URL or "redis://redis:6379/0", decode_responses=True)


@lru_cache()
def get_document_repository() -> DocumentRepository:
    return DocumentRepository(get_elasticsearch_client())


@lru_cache()
def get_cache_repository() -> CacheRepository:
    return CacheRepository(get_redis_client())


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache()
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        document_repo=get_document_repository(),
        cache_repo=get_cache_repository(),
        embedding_service=get_embedding_service(),
    )
