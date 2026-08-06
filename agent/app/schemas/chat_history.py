from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime



class BaseChatHistory(BaseModel):
    question: str = Field(..., description="The question asked by the user")
    answer: str = Field(..., description="The answer provided by the model")



class ChatHistoryRequest(BaseChatHistory):
    user_id: UUID = Field(..., description="The ID of the user who asked the question")
    session_id: UUID = Field(..., description="The ID of the session in which the question was asked")
    timestamp: datetime = Field(default_factory=datetime.now, description="The time when the question was asked")

    class Config:
        from_attributes = True



class ChatHistoryResponse(BaseChatHistory):
    id: UUID = Field(..., description="The unique identifier for the chat history entry")
    user_id: UUID = Field(..., description="The ID of the user who asked the question")
    session_id: UUID = Field(..., description="The ID of the session in which the question was asked")
    timestamp: datetime = Field(..., description="The time when the question was asked")

    class Config:
        from_attributes = True