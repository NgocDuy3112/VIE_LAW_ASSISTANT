from fastapi import APIRouter, Depends
from qdrant_client import AsyncQdrantClient

from modules.documents.helpers.caching import ValkeySemanticCache
from modules.documents.schemas.retrieve import RetrieveRequest, RetrieveResponse
from modules.documents.core.v1.retrieve import retriever_service
from modules.documents.dependencies import get_async_qdrant_client, get_valkey_cache



retrieve_router = APIRouter(prefix="/v1/retrieve")



@retrieve_router.post("/", response_model=RetrieveResponse, operation_id="retrieve_documents")
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
        request,
    )