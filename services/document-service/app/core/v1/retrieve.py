import numpy as np
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import *

from app.helpers.caching import ValkeySemanticCache
from app.helpers.embedding import DenseEmbeddingService
from app.helpers.sparse_embedding import SparseEmbeddingService
from app.helpers.extract_keywords import extract_legal_keywords
from app.schemas.document import DocumentSchema
from app.schemas.retrieve import RetrieveRequest, RetrieveResponse
from app.log.logger import get_logger
from app.config import settings


logger = get_logger(__name__)
dense_embedding = DenseEmbeddingService()
sparse_embedding = SparseEmbeddingService()



class Retriever:
    """
    Retriever: first check Valkey semantic cache, then fallback to Qdrant.
    Returns validated DocumentSchema objects.
    """
    def __init__(
        self,
        async_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(url=settings.QDRANT_CLIENT_URL),
        valkey_cache: ValkeySemanticCache = ValkeySemanticCache(),
        collection_name: str = settings.QDRANT_COLLECTION_NAME,
        cache_threshold: float = 0.8,
    ):
        self.cache = valkey_cache
        self.qdrant = async_qdrant_client
        self.collection = collection_name
        self.cache_threshold = cache_threshold

    async def retrieve(
        self,
        dense_vector: np.ndarray,
        sparse_vector: dict[str, list],
        top_k: int = 3,
        filter: Filter | None = None
    ) -> list[DocumentSchema]:
        logger.debug("Starting retrieval: top_k=%d, filter=%s", top_k, filter)

        # Attempt to retrieve cached documents
        cached_docs = await self.cache.search(dense_vector, top_k=top_k)

        if cached_docs:
            logger.info("✅ Cache hit: retrieved %d docs from Valkey", len(cached_docs))
            documents = []
            for item in cached_docs:
                metadata = item.get("payload", {}).get("metadata", {})
                documents.append(
                    DocumentSchema(
                        id=metadata.get("id", ""),
                        metadata=metadata
                    )
                )
            return documents

        logger.info("❌ Cache miss → querying Qdrant...")

        result = await self.qdrant.query_points(
            collection_name=self.collection,
            prefetch=[
                Prefetch(
                    query=SparseVector(
                        indices=sparse_vector["indices"], 
                        values=sparse_vector["values"]
                    ),
                    using="text-sparse",
                    limit=20
                ),
                Prefetch(
                    query=dense_vector,
                    using="text-dense",
                    limit=20
                )
            ],
            query=FusionQuery(fusion=Fusion.RRF),
            limit=top_k,
            with_payload=True,
            with_vectors=False,
            query_filter=filter,
            search_params=SearchParams(
                quantization=models.QuantizationSearchParams(oversampling=2)
            )
        )
        points = result.points
        docs: list[DocumentSchema] = []
        for hit in points:
            doc = DocumentSchema(
                id=hit.id,
                metadata=hit.payload
            )
            docs.append(doc)
            logger.debug("Retrieved doc ID=%s from Qdrant", id)

            await self.cache.set(
                text=hit.payload.get("content", ""),
                embedding=dense_vector,
                payload=hit.payload
            )
            logger.debug("Added doc ID=%s to Valkey cache", id)

        logger.info("✅ Qdrant returned %d docs", len(docs))
        return docs



def build_keyword_inclusion_filter(keywords: list[str], field_name="content") -> Filter:
    return Filter(
        should=[
            FieldCondition(
                key=field_name,
                match=MatchPhrase(phrase=kw)
            )
            for kw in keywords
        ]
    )



async def retriever_service(
    async_qdrant_client: AsyncQdrantClient, 
    valkey_cache: ValkeySemanticCache, 
    request: RetrieveRequest
) -> RetrieveResponse:
    try:
        retriever = Retriever(async_qdrant_client, valkey_cache)
        dense_vector = dense_embedding.embed_query(request.query)
        sparse_vector = sparse_embedding.embed_query(request.query)
        include_keywords = extract_legal_keywords(request.query)
        include_filter = build_keyword_inclusion_filter(include_keywords)
        documents = await retriever.retrieve(dense_vector, sparse_vector, request.top_k, include_filter)
        return RetrieveResponse(
            results=documents,
            status='success',
            detail=f"Successfully retrieved {len(documents)} documents."
        )
    except Exception as e:
        return RetrieveResponse(
            results=[],
            status='error',
            detail=f"Retrieving process got error: {e}"
        )