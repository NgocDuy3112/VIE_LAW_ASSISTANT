from qdrant_client import AsyncQdrantClient
from qdrant_client.models import *
from config import settings


from log.logger import get_logger

logger = get_logger(__name__)



async def init_qdrant_collection(collection_name: str = settings.QDRANT_COLLECTION_NAME) -> None:
    try:
        client = AsyncQdrantClient(url=settings.QDRANT_CLIENT_URL)
        collections = await client.get_collections()
        existing = [col.name for col in collections.collections]

        if collection_name not in existing:
            logger.info(f"🔧 Creating collection '{collection_name}'")
            await client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "text-dense": VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE,
                        datatype=Datatype.FLOAT16
                    )
                },
                quantization_config=BinaryQuantization(
                    binary=BinaryQuantizationConfig(
                        encoding=BinaryQuantizationEncoding.TWO_BITS,
                        query_encoding=BinaryQuantizationQueryEncoding.BINARY,
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