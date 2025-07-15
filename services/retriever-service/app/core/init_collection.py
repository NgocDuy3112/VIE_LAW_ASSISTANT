from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config import QDRANT_CLIENT_URL, QDRANT_COLLECTION_NAME, EMBEDDING_DIMENSION


from log.logger import get_logger

logger = get_logger(__name__)



async def init_qdrant_collection():
    try:
        client = AsyncQdrantClient(url=QDRANT_CLIENT_URL)
        collections = await client.get_collections()
        existing = [col.name for col in collections.collections]

        if QDRANT_COLLECTION_NAME not in existing:
            logger.info(f"🔧 Creating collection '{QDRANT_COLLECTION_NAME}'")
            await client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection '{QDRANT_COLLECTION_NAME}' created successfully")
        else:
            logger.info(f"✅ Collection '{QDRANT_COLLECTION_NAME}' already exists")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant collection: {e}")
        raise
    finally:
        await client.close()