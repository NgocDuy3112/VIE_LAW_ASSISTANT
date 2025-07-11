from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


class AskResponse(BaseModel):
    role: str
    content: str