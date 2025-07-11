from fastapi import APIRouter, Depends
from qdrant_client import AsyncQdrantClient
from app.schemas.document import DocumentSchema
from app.services.v1.indexing import indexing_service
from app.dependencies import get_async_qdrant_client  # use the Depends



indexing_router = APIRouter(prefix="/v1/index")


@indexing_router.post("/", response_model=DocumentSchema)
async def index_document(
    document: DocumentSchema,
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client)
):
    """
    Index a document into Qdrant and return it.
    """
    return await indexing_service(document, async_qdrant_client)