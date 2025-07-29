import aiohttp
from qdrant_client import AsyncQdrantClient
from app.helpers.caching import ValkeySemanticCache
from app.schemas.ask import AskRequest, AskResponse
from app.core.v1.retriever import Retriever, build_keyword_inclusion_filter
from app.helpers.embedding import DenseEmbeddingService
from app.helpers.sparse_embedding import SparseEmbeddingService
from app.log.logger import get_logger
from app.config import QDRANT_CLIENT_URL, QDRANT_COLLECTION_NAME, LLM_SERVICE_URL


logger = get_logger(__name__)


dense_embedding = DenseEmbeddingService()
sparse_embedding = SparseEmbeddingService()


async def create_ask_service(
    request: AskRequest,
    async_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(url=QDRANT_CLIENT_URL),
    valkey_cache: ValkeySemanticCache = ValkeySemanticCache(),
) -> AskResponse:
    logger.info("🚀 ask_service started with question: %s", request.question)

    # Step 1: Embed question
    dense_vector = dense_embedding.embed_query(request.question)
    sparse_vector = sparse_embedding.embed_query(request.question)
    logger.debug("✅ Embedding generated: %s...", str(dense_vector)[:60])

    # Step 2: Retrieve top_k docs
    retriever = Retriever(
        async_qdrant_client=async_qdrant_client,
        valkey_cache=valkey_cache,
        collection_name=QDRANT_COLLECTION_NAME
    )
    retrieved_docs = await retriever.retrieve(
        dense_vector=dense_vector,
        sparse_vector=sparse_vector,
        top_k=request.top_k,
        # filter=build_keyword_inclusion_filter()
    )
    logger.info("📄 Retrieved %d docs from retriever", len(retrieved_docs))

    # Step 3: Build prompt with context
    context = "\n\n".join(
        f"- {doc.metadata.get('content','')}" for doc in retrieved_docs
    )
    final_prompt = f"Context:\n{context}\n\nQuestion: {request.question}"
    logger.debug("📝 Final prompt: %s...", final_prompt[:200])

    # Call LLM service with aiohttp
    payload = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "Bạn là trợ lý pháp luật, trả lời ngắn gọn và chính xác."
                }
                
            ]
        },
        {
            "role": "user", 
            "content": [
                {
                    "type": "text",
                    "text": final_prompt
                }
            ]
        }
    ]

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{LLM_SERVICE_URL}/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            data: dict = await response.json()

    return AskResponse(role=data["role"], content=data["content"])