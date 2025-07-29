from qdrant_client import AsyncQdrantClient, models
from app.helpers.embedding import DenseEmbeddingService
from app.helpers.sparse_embedding import SparseEmbeddingService
from app.helpers.pdf_processor import PDFProcessor, calculate_content_hash
from app.schemas.document import DocumentSchema
from app.log.logger import get_logger
from app.config import QDRANT_CLIENT_URL, QDRANT_COLLECTION_NAME


logger = get_logger(__name__)
dense_embedding = DenseEmbeddingService()
sparse_embedding = SparseEmbeddingService()



async def is_document_already_indexed(async_qdrant_client: AsyncQdrantClient, content_hash: str) -> bool:
    scroll = await async_qdrant_client.scroll(
        collection_name=QDRANT_COLLECTION_NAME,
        scroll_filter=models.Filter(
            must=[models.FieldCondition(
                key="content_hash",
                match=models.MatchValue(value=content_hash)
            )]
        ),
        limit=1
    )
    return bool(scroll and scroll[0])  # scroll returns (points, next_page)




async def create_indexing_service(
    document: DocumentSchema,
    async_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(url=QDRANT_CLIENT_URL)
):
    content = document.metadata.get("content", "")
    content_hash = calculate_content_hash(content)
    if await is_document_already_indexed(async_qdrant_client, content_hash):
        logger.info(f"✅ Document already indexed (hash={content_hash}), skipping.")
        return document

    logger.info(f"🔄 Indexing new document (hash={content_hash})")
    # Get embedding steps
    dense_vector = dense_embedding.embed_document(document)
    sparse_vector = sparse_embedding.embed_document(document)
    
    payload = dict(document.metadata)
    payload["file_hash"] = content_hash

    await async_qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=str(document.id),
                payload=document.metadata,
                vector={
                    "text-dense": dense_vector,
                    "text-sparse": {
                        "indices": sparse_vector["indices"],
                        "values": sparse_vector["values"]
                    }
                }
            )
        ]
    )
    return document




async def create_indexing_service_from_pdf(
    pdf_file: str,
    async_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(url=QDRANT_CLIENT_URL)
) -> list[DocumentSchema]:
    processor = PDFProcessor(pdf_file)
    documents = processor.extract_documents()
    indexed_docs = []

    for document in documents:
        content = document.metadata.get("content", "")
        content_hash = calculate_content_hash(content)

        if await is_document_already_indexed(async_qdrant_client, content_hash):
            logger.info(f"✅ Skipping already indexed doc (hash={content_hash})")
            continue

        logger.info(f"🔄 Indexing new doc from PDF (hash={content_hash})")
        vector = dense_embedding.embed_document(document)

        payload = dict(document.metadata)
        payload["content_hash"] = content_hash

        await async_qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(document.id),
                    payload=payload,
                    vector=vector
                )
            ]
        )
        indexed_docs.append(document)
    return indexed_docs