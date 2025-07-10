from pydantic import BaseModel, Field


class BaseMessageSchema(BaseModel):
    role: str = Field(..., description="Role of the message sender (e.g., 'user', 'assistant')")
    content: list[dict] = Field(..., description="Content of the message")



class Message(BaseMessageSchema):
    """
    Represents a message in a conversation.
    Inherits from BaseMessageSchema to ensure all messages have a role and content.
    """
    pass