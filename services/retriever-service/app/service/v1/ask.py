import aiohttp
from qdrant_client import AsyncQdrantClient
from app.helpers.caching import ValkeySemanticCache
from app.schemas.ask import AskRequest, AskResponse
from app.service.v1.retriever import HybridRetriever
from app.helpers.embedding import embed_query
from app.log.logger import get_logger
from app.config import QDRANT_CLIENT_URL, QDRANT_COLLECTION_NAME, LLM_SERVICE_URL


logger = get_logger(__name__)



async def create_ask_service(
    request: AskRequest,
    async_qdrant_client: AsyncQdrantClient = AsyncQdrantClient(url=QDRANT_CLIENT_URL),
    valkey_cache: ValkeySemanticCache = ValkeySemanticCache(),
) -> AskResponse:
    logger.info("🚀 ask_service started with question: %s", request.question)

    # Step 1: Embed question
    query_embedding = embed_query(request.question)
    logger.debug("✅ Embedding generated: %s...", str(query_embedding)[:60])

    # Step 2: Retrieve top_k docs
    # Step 2: Retrieve top_k docs
    retriever = HybridRetriever(
        async_valkey_cache=valkey_cache,
        async_qdrant_client=async_qdrant_client,
        collection_name=QDRANT_COLLECTION_NAME
    )
    retrieved_docs = await retriever.retrieve(
        query_embedding=query_embedding,
        top_k=request.top_k,
        filter=request.filter
    )
    logger.info("📄 Retrieved %d docs from retriever", len(retrieved_docs))

    # Step 3: Build prompt with context
    context = "\n\n".join(
        f"- {doc.metadata.get('content','')}" for doc in retrieved_docs
    )
    final_prompt = f"Context:\n{context}\n\nQuestion: {request.question}"
    logger.debug("📝 Final prompt: %s...", final_prompt[:200])

    # Step 4: Call LLM service with aiohttp
    payload = {
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý pháp luật, trả lời ngắn gọn và chính xác."},
            {"role": "user", "content": final_prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{LLM_SERVICE_URL}/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            data = await response.json()

    answer = AskResponse(*data)
    return answer