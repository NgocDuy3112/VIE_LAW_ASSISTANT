from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Any
import jwt

from app.config import settings


SECRET = settings.AUTH_HS256_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS



def create_access_token(subject: str, scopes: list | None = None) -> str:
    now = datetime.now()
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    if scopes:
        payload["scopes"] = scopes
    return jwt.encode(payload, SECRET, algorithm="HS256")



def create_refresh_token() -> dict[str, Any]:
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    issued_at = datetime.now()
    expires_at = issued_at + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return {"token": raw, "token_hash": token_hash, "issued_at": issued_at, "expires_at": expires_at}



def verify_access_token(token: str) -> dict[str, Any]:
    # raises jwt exceptions if invalid/expired
    return jwt.decode(token, SECRET, algorithms=["HS256"])



def get_token_hash(raw_token: str) -> str:
    """Calculates the SHA256 hash of the raw token string."""
    return hashlib.sha256(raw_token.encode()).hexdigest()