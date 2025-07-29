from pydantic import BaseModel, Field
from uuid import UUID, uuid4


def create_uuid_string():
    return str(uuid4())


class DocumentSchema(BaseModel):
    id: str = Field(default_factory=create_uuid_string, description="Unique identifier for the document")
    metadata: dict = Field(default_factory=dict, description="Metadata associated with the document")