from typing import Literal
from pydantic import BaseModel, Field


class BaseMessageSchema(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Role of the message sender (e.g., 'user', 'assistant', 'system')")
    content: str = Field(..., description="Content of the message")



class Message(BaseMessageSchema):
    """
    Represents a message in a conversation.
    Inherits from BaseMessageSchema to ensure all messages have a role and content.
    """
    pass