import pytest
import asyncio
from fastapi import status
from aiohttp import ClientSession
from unittest.mock import patch, AsyncMock
from app.schemas.message import Message


BASE_URL = 'http://localhost:8001'


@pytest.mark.asyncio
async def test_create_chat_completion_success():
    test_message = Message(role="user", content=[{"role": "user", "content": "Hello"}])
    expected_response = Message(role="assistant", content=[{"role": "assistant", "content": "Hi!"}])
    with patch(
        "app.core.chat_completions.create_chat_completion", 
        new=AsyncMock(return_value=expected_response)
    ):
        async with ClientSession() as session:
            async with session.post(f"{BASE_URL}/v1/chat/completions", json=[test_message.model_dump()]) as response:
                resp_json = await response.json()
    assert response.status == status.HTTP_200_OK
    assert resp_json["role"] == "assistant"


@pytest.mark.asyncio
async def test_create_chat_completion_empty_body():
    async with ClientSession() as session:
        async with session.post(f"{BASE_URL}/v1/chat/completions", json=[]) as response:
            resp_json = await response.json()
    assert response.status == status.HTTP_400_BAD_REQUEST
    assert resp_json["detail"] == "Messages cannot be empty."


@pytest.mark.asyncio
async def test_create_chat_completion_timeout():
    test_message = Message(role="user", content=[{"role": "user", "content": "Hello"}])
    with patch(
        "app.core.chat_completions.create_chat_completion", 
        new=AsyncMock(side_effect=asyncio.TimeoutError)
    ):
        async with ClientSession() as session:
            async with session.post(f"{BASE_URL}/v1/chat/completions", json=[test_message.model_dump()]) as response:
                resp_json = await response.json()
    assert response.status == status.HTTP_504_GATEWAY_TIMEOUT
    assert resp_json["detail"] == "Request timed out. Please try again later."


@pytest.mark.asyncio
async def test_create_chat_completion_rate_limit():
    from fastapi import HTTPException
    with patch(
        "app.api.chat_completions.limiter.limit", 
        side_effect=HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later.")
        ):
        test_message = Message(role="user", content=[{"role": "user", "content": "Hello"}])
        async with ClientSession() as session:
            async with session.post(f"{BASE_URL}/v1/chat/completions", json=[test_message.model_dump()]) as response:
                text = await response.text()
        assert response.status == status.HTTP_429_TOO_MANY_REQUESTS
        assert "rate limit exceeded" in text.lower()