from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: str
    title: str | None
    created_at: str
