from typing import Literal, TypedDict

from graph.llm import ChatMessage


class AgentState(TypedDict, total=False):
    messages: list[ChatMessage]
    next: Literal["response", "rag"]
    documents: list[str]
