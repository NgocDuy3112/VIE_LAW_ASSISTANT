from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


class JWTService:
    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid JWT token: %s", e)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user_id from JWT token."""
    payload = JWTService.verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return user_id
