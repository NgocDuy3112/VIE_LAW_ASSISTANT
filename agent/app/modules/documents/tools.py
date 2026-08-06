from modules.documents.core.v1.retrieve import retriever_service
from modules.documents.dependencies import get_async_qdrant_client, get_valkey_cache
from modules.documents.schemas.retrieve import RetrieveRequest


async def retrieve_document(query: str, top_k: int = 5) -> list[str]:
    response = await retriever_service(
        get_async_qdrant_client(),
        get_valkey_cache(),
        RetrieveRequest(query=query, top_k=top_k),
    )
    if response.status == "error":
        return [response.detail or "Document retrieval failed."]

    if not response.results:
        return ["No relevant documents found."]

    documents: list[str] = []
    for index, document in enumerate(response.results, start=1):
        content = document.metadata.get("content", document.metadata)
        source = document.metadata.get("source") or document.metadata.get("file_name") or document.id
        documents.append(f"[{index}] Source: {source}\n{content}")
    return documents
