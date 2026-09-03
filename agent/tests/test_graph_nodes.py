"""Unit tests for graph.nodes (route / RAG / response nodes).

The LLM is replaced by a fake implementation — no HTTP calls are made.
"""

import pytest

from graph.nodes import make_rag_node, make_response_node, route_node


class FakeChatModel:
    """Deterministic stand-in for ChatModel."""

    def __init__(self, route_decision: str = "rag", completion: str = "Câu trả lời giả lập."):
        self.route_decision = route_decision
        self.completion = completion
        self.complete_calls: list[list[dict]] = []

    async def route(self, messages: list[dict]) -> str:
        return self.route_decision

    async def complete(self, messages: list[dict]) -> str:
        self.complete_calls.append(messages)
        return self.completion


@pytest.fixture
def llm():
    return FakeChatModel()


class TestRouteNode:
    async def test_returns_route_from_llm(self, llm):
        state = {"messages": [{"role": "user", "content": "Điều 3 quy định gì?"}]}

        result = await route_node(state, llm)

        assert result == {"route": "rag"}

    async def test_route_response_when_no_retrieval_needed(self):
        llm = FakeChatModel(route_decision="response")
        state = {"messages": [{"role": "user", "content": "Xin chào"}]}

        result = await route_node(state, llm)

        assert result == {"route": "response"}

    async def test_route_with_empty_messages(self, llm):
        result = await route_node({}, llm)

        assert result == {"route": "rag"}


class TestRagNode:
    async def test_uses_last_user_message_as_query(self):
        retrieved: list[str] = []

        async def fake_retrieve(query: str) -> list[str]:
            retrieved.append(query)
            return ["[1] Source: law.pdf\nĐiều 1..."]

        node = make_rag_node(fake_retrieve)
        state = {
            "messages": [
                {"role": "user", "content": "Câu hỏi đầu"},
                {"role": "assistant", "content": "Trả lời đầu"},
                {"role": "user", "content": "Câu hỏi sau"},
            ]
        }

        result = await node(state)

        assert retrieved == ["Câu hỏi sau"]
        assert result == {"documents": ["[1] Source: law.pdf\nĐiều 1..."]}

    async def test_empty_state_retrieves_with_empty_query(self):
        queries: list[str] = []

        async def fake_retrieve(query: str) -> list[str]:
            queries.append(query)
            return []

        node = make_rag_node(fake_retrieve)

        result = await node({})

        assert queries == [""]
        assert result == {"documents": []}


class TestResponseNode:
    async def test_builds_system_prompt_with_documents(self, llm):
        node = make_response_node(llm)
        state = {
            "messages": [{"role": "user", "content": "Điều 1 quy định gì?"}],
            "documents": ["[1] Source: law.pdf\nĐiều 1: ..."],
        }

        result = await node(state)

        assert result["answer"] == {"role": "assistant", "content": "Câu trả lời giả lập."}
        sent_messages = llm.complete_calls[0]
        assert sent_messages[0]["role"] == "system"
        assert "[1] Source: law.pdf\nĐiều 1: ..." in sent_messages[0]["content"]
        assert sent_messages[1:] == state["messages"]

    async def test_works_without_documents(self, llm):
        node = make_response_node(llm)
        state = {"messages": [{"role": "user", "content": "Xin chào"}]}

        result = await node(state)

        system_content = llm.complete_calls[0][0]["content"]
        assert "Tài liệu:\n" in system_content
        assert result["answer"]["content"] == "Câu trả lời giả lập."

    async def test_multiple_documents_are_joined(self, llm):
        node = make_response_node(llm)
        state = {
            "messages": [{"role": "user", "content": "q"}],
            "documents": ["doc-a", "doc-b"],
        }

        await node(state)

        system_content = llm.complete_calls[0][0]["content"]
        assert "doc-a\n\ndoc-b" in system_content
