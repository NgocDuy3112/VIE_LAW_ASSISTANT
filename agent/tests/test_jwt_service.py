"""Unit tests for modules.auth.jwt_service (JWTService + get_current_user)."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException

from config import settings
from modules.auth.jwt_service import JWTService, get_current_user

USER_ID = "11111111-1111-1111-1111-111111111111"


def make_token(payload: dict) -> str:
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class TestVerifyToken:
    def test_valid_token_returns_payload(self):
        token = make_token({"sub": USER_ID, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)})

        payload = JWTService.verify_token(token)

        assert payload["sub"] == USER_ID

    def test_expired_token_raises_401(self):
        token = make_token({"sub": USER_ID, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)})

        with pytest.raises(HTTPException) as exc_info:
            JWTService.verify_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token expired"

    def test_token_expired_without_signature_exp_claim(self):
        # exp in payload but signed without ExpiredSignatureError path
        token = make_token({"sub": USER_ID, "exp": int((datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp())})

        with pytest.raises(HTTPException) as exc_info:
            JWTService.verify_token(token)

        assert exc_info.value.status_code == 401

    def test_invalid_signature_raises_401(self):
        token = jwt.encode({"sub": USER_ID}, "wrong-secret", algorithm="HS256")

        with pytest.raises(HTTPException) as exc_info:
            JWTService.verify_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_malformed_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            JWTService.verify_token("not-a-jwt")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"

    def test_token_without_exp_is_accepted(self):
        token = make_token({"sub": USER_ID})

        payload = JWTService.verify_token(token)

        assert payload["sub"] == USER_ID


class TestGetCurrentUser:
    async def test_returns_sub_from_valid_token(self):
        credentials = MagicMock()
        credentials.credentials = make_token({"sub": USER_ID})

        user_id = await get_current_user(credentials)

        assert user_id == USER_ID

    async def test_missing_sub_raises_401(self):
        credentials = MagicMock()
        credentials.credentials = make_token({"role": "user"})

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token payload"
