from modules.documents.dependencies import get_retrieval_service
from modules.documents.schemas.retrieve import RetrieveRequest


async def retrieve_document(query: str, top_k: int = 5) -> list[str]:
    service = get_retrieval_service()
    response = await service.retrieve(RetrieveRequest(query=query, top_k=top_k))

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
