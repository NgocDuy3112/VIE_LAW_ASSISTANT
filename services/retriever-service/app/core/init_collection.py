from qdrant_client import AsyncQdrantClient
from qdrant_client.models import *
from app.config import QDRANT_CLIENT_URL, QDRANT_COLLECTION_NAME, EMBEDDING_DIMENSION


from log.logger import get_logger

logger = get_logger(__name__)



async def init_qdrant_collection(collection_name: str = QDRANT_COLLECTION_NAME) -> None:
    try:
        client = AsyncQdrantClient(url=QDRANT_CLIENT_URL)
        collections = await client.get_collections()
        existing = [col.name for col in collections.collections]

        if collection_name not in existing:
            logger.info(f"🔧 Creating collection '{collection_name}'")
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                    datatype=Datatype.FLOAT16
                ),
                quantization_config=models.BinaryQuantization(
                    binary=models.BinaryQuantizationConfig(
                        encoding=models.BinaryQuantizationEncoding.TWO_BITS,
                        query_encoding=models.BinaryQuantizationQueryEncoding.BINARY,
                        always_ram=False,
                    ),
                ),
            )
            logger.info(f"✅ Collection '{collection_name}' created successfully")
        else:
            logger.info(f"✅ Collection '{collection_name}' already exists")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant collection: {e}")
        raise
    finally:
        await client.close()