from graph.llm import ChatMessage, ChatModel
from modules.documents.tools import retrieve_document


supervisor_llm = ChatModel("ollama/qwen3:1.7b", temperature=0.1)
response_llm = ChatModel("lmstudio/seallms-v3-1.5b-chat", temperature=0.1)


async def agent_invoke(messages: list[ChatMessage]) -> ChatMessage:
    route = await supervisor_llm.route(messages)

    documents: list[str] = []
    if route == "rag":
        last_user_message = next(
            (message["content"] for message in reversed(messages) if message.get("role") == "user"),
            "",
        )
        documents = await retrieve_document(last_user_message)

    document_context = "\n\n".join(documents)
    response_messages: list[ChatMessage] = [
        {
            "role": "system",
            "content": (
                "Bạn là trợ lý pháp luật Việt Nam. Trả lời ngắn gọn, chính xác. "
                "Nếu có tài liệu được cung cấp, ưu tiên dựa trên tài liệu đó.\n\n"
                f"Tài liệu:\n{document_context}"
            ),
        },
        *messages,
    ]
    content = await response_llm.complete(response_messages)
    return {"role": "assistant", "content": content}
