"""Unit tests for modules.chat.services.chat_service.ChatService.

Repositories are mocked — no database is touched.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from modules.chat.services.chat_service import ChatService

USER_ID = "11111111-1111-1111-1111-111111111111"
SESSION_ID = "22222222-2222-2222-2222-222222222222"


@pytest.fixture
def session_repo():
    repo = AsyncMock()
    repo.create.return_value = {"id": SESSION_ID, "user_id": USER_ID, "title": None}
    repo.get_by_id.return_value = {"id": SESSION_ID, "user_id": USER_ID}
    repo.get_by_user.return_value = [{"id": SESSION_ID, "user_id": USER_ID}]
    repo.delete.return_value = True
    return repo


@pytest.fixture
def message_repo():
    repo = AsyncMock()
    repo.create.return_value = {"id": "33333333-3333-3333-3333-333333333333", "role": "user", "content": "Hello"}
    repo.get_by_session.return_value = [
        SimpleNamespace(role="user", content="Hello"),
        SimpleNamespace(role="assistant", content="Hi!"),
    ]
    return repo


@pytest.fixture
def service(session_repo, message_repo):
    return ChatService(session_repo=session_repo, message_repo=message_repo)


class TestChatServiceSessions:
    async def test_create_session_delegates_to_repo(self, service, session_repo):
        result = await service.create_session(USER_ID, title="Luật đất đai")

        session_repo.create.assert_awaited_once_with(USER_ID, "Luật đất đai")
        assert result["id"] == SESSION_ID

    async def test_create_session_without_title(self, service, session_repo):
        await service.create_session(USER_ID)

        session_repo.create.assert_awaited_once_with(USER_ID, None)

    async def test_get_session(self, service, session_repo):
        result = await service.get_session(SESSION_ID)

        session_repo.get_by_id.assert_awaited_once_with(SESSION_ID)
        assert result["user_id"] == USER_ID

    async def test_get_sessions_by_user(self, service, session_repo):
        result = await service.get_sessions_by_user(USER_ID)

        session_repo.get_by_user.assert_awaited_once_with(USER_ID)
        assert len(result) == 1

    async def test_delete_session_returns_repo_result(self, service, session_repo):
        assert await service.delete_session(SESSION_ID) is True

        session_repo.delete.assert_awaited_once_with(SESSION_ID)

    async def test_delete_missing_session_returns_false(self, service, session_repo):
        session_repo.delete.return_value = False

        assert await service.delete_session("99999999-9999-9999-9999-999999999999") is False


class TestChatServiceMessages:
    async def test_add_message_delegates_to_repo(self, service, message_repo):
        result = await service.add_message(SESSION_ID, "user", "Hello")

        message_repo.create.assert_awaited_once_with(SESSION_ID, "user", "Hello")
        assert result["content"] == "Hello"

    async def test_get_messages(self, service, message_repo):
        result = await service.get_messages(SESSION_ID)

        message_repo.get_by_session.assert_awaited_once_with(SESSION_ID)
        assert len(result) == 2

    async def test_get_history_for_agent_maps_role_and_content(self, service, message_repo):
        history = await service.get_history_for_agent(SESSION_ID)

        assert history == [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]

    async def test_get_history_for_agent_empty_session(self, service, message_repo):
        message_repo.get_by_session.return_value = []

        assert await service.get_history_for_agent(SESSION_ID) == []
