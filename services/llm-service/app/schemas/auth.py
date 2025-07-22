from pydantic import BaseModel
from uuid import UUID



class UserClaims(BaseModel):
    user_id: UUID
    username: str | None = None
    exp: int