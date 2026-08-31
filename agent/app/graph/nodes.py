from collections.abc import Awaitable, Callable
from graph.llm import ChatMessage, ChatModel
from graph.state import AgentState


async def route_node(state: AgentState, llm: ChatModel) -> AgentState:
    return {"route": await llm.route(state.get("messages", []))}


def make_rag_node(retrieve_documents: Callable[[str], Awaitable[list[str]]]):
    async def rag_node(state: AgentState) -> AgentState:
        query = next(
            (message["content"] for message in reversed(state.get("messages", [])) if message.get("role") == "user"),
            "",
        )
        return {"documents": await retrieve_documents(query)}

    return rag_node


def make_response_node(llm: ChatModel):
    async def response_node(state: AgentState) -> AgentState:
        documents = "\n\n".join(state.get("documents", []))
        messages: list[ChatMessage] = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý pháp luật Việt Nam. Trả lời ngắn gọn, chính xác. "
                    "Nếu có tài liệu được cung cấp, ưu tiên dựa trên tài liệu đó.\n\n"
                    f"Tài liệu:\n{documents}"
                ),
            },
            *state.get("messages", []),
        ]
        return {"answer": {"role": "assistant", "content": await llm.complete(messages)}}

    return response_node
