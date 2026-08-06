from collections.abc import Awaitable, Callable

from graph.llm import ChatMessage, ChatModel
from graph.state import AgentState


def make_rag_agent(retrieve_documents: Callable[[str], Awaitable[list[str]]]):
    async def rag_agent(state: AgentState) -> AgentState:
        last_user_message = next(
            (message["content"] for message in reversed(state.get("messages", [])) if message.get("role") == "user"),
            "",
        )
        return {"documents": await retrieve_documents(last_user_message), "next": "response"}
    return rag_agent


def make_response_node(llm: ChatModel):
    async def response_node(state: AgentState) -> ChatMessage:
        documents = "\n\n".join(state.get("documents", []))
        messages: list[ChatMessage] = [
            {
                "role": "system",
                "content": f"Bạn là trợ lý pháp luật Việt Nam. Trả lời dựa trên tài liệu nếu có.\n\nTài liệu:\n{documents}",
            },
            *state.get("messages", []),
        ]
        return {"role": "assistant", "content": await llm.complete(messages)}
    return response_node
