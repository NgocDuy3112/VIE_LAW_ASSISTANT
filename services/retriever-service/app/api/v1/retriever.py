from fastapi import APIRouter, Depends
from qdrant_client import AsyncQdrantClient
from app.helpers.caching import ValkeySemanticCache
from app.schemas.document import DocumentSchema
from app.schemas.retrieve import RetrieveRequest
from app.services.v1.retriever import retriever_service
from app.dependencies import get_async_qdrant_client, get_valkey_cache



retriever_router = APIRouter(prefix="/v1/retrieve")



@retriever_router.post("/", response_model=list[DocumentSchema])
async def retrieve(
    request: RetrieveRequest,
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client),
    valkey_cache: ValkeySemanticCache = Depends(get_valkey_cache)
):
    """
    Retrieve top_k relevant documents based on a query & optional filter.
    """
    return await retriever_service(
        async_qdrant_client,
        valkey_cache,
        query=request.query,
        top_k=request.top_k,
        filter=request.filter
    )