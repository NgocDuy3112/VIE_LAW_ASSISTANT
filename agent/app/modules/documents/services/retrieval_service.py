import numpy as np

from modules.documents.repositories.document_repository import DocumentRepository
from modules.documents.repositories.cache_repository import CacheRepository
from modules.documents.services.embedding_service import EmbeddingService
from modules.documents.helpers.extract_keywords import extract_legal_keywords
from modules.documents.schemas.document import DocumentSchema
from modules.documents.schemas.retrieve import RetrieveRequest, RetrieveResponse
from app.logger import get_logger

logger = get_logger(__name__)


class RetrievalService:
    """Orchestrates document retrieval using repositories and embedding."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        cache_repo: CacheRepository,
        embedding_service: EmbeddingService,
    ):
        self.document_repo = document_repo
        self.cache_repo = cache_repo
        self.embedding = embedding_service

    async def retrieve(self, request: RetrieveRequest) -> RetrieveResponse:
        try:
            dense_vector = await self.embedding.embed(request.query)
            keywords = extract_legal_keywords(request.query)
            documents = await self._search(request.query, dense_vector, request.top_k, keywords, request.filter)
            return RetrieveResponse(
                results=documents,
                status="success",
                detail=f"Successfully retrieved {len(documents)} documents.",
            )
        except Exception as exc:
            logger.exception("Retrieval failed")
            return RetrieveResponse(results=[], status="error", detail=f"Retrieval error: {exc}")

    async def _search(self, query: str, dense_vector: np.ndarray, top_k: int, keywords: list[str], filters: dict | None) -> list[DocumentSchema]:
        # Check cache first
        cached = await self.cache_repo.search(dense_vector, top_k=top_k)
        if cached:
            logger.info("Cache hit: %d documents", len(cached))
            return [DocumentSchema(id=str(item["payload"].get("id", "")), metadata=item["payload"]) for item in cached]

        # Build keyword filter
        keyword_filter = None
        if keywords:
            keyword_filter = {"bool": {"should": [{"match_phrase": {"content": kw}} for kw in keywords], "minimum_should_match": 1}}

        # Merge filters
        combined_filter = None
        if filters and keyword_filter:
            combined_filter = {"bool": {"must": [filters, keyword_filter]}}
        elif filters:
            combined_filter = filters
        elif keyword_filter:
            combined_filter = keyword_filter

        # Hybrid search: BM25 + dense vector
        lexical_hits = await self.document_repo.search_lexical(query, size=top_k * 2, filters=combined_filter)
        semantic_hits = await self.document_repo.search_semantic(dense_vector.tolist(), size=top_k * 2)

        # RRF fusion
        merged = {}
        for rank, hit in enumerate(lexical_hits):
            merged.setdefault(hit["_id"], {"hit": hit, "score": 0})["score"] += 1 / (60 + rank + 1)
        for rank, hit in enumerate(semantic_hits):
            merged.setdefault(hit["_id"], {"hit": hit, "score": 0})["score"] += 1 / (60 + rank + 1)

        results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:top_k]
        documents = [DocumentSchema(id=item["hit"]["_id"], metadata=item["hit"]["_source"]) for item in results]

        # Cache results
        for doc in documents:
            await self.cache_repo.set(doc.metadata.get("content", ""), dense_vector, doc.metadata)

        return documents
