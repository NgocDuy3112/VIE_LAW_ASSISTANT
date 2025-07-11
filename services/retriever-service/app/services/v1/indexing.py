from qdrant_client import AsyncQdrantClient, models
from app.helpers.embedding import *
from app.schemas.document import DocumentSchema
from app.log.logger import get_logger
from app.config import QDRANT_CLIENT_URL, QDRANT_COLLECTION_NAME


logger = get_logger(__name__)


async def indexing_service(
    document: DocumentSchema,
    async_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(url=QDRANT_CLIENT_URL)
):
    vector = embed_document(document)
    async_qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=document.id,
                payload=document.metadata,
                vector=vector
            )
        ]
    )