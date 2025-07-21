from pydantic import BaseModel, Field, field_validator
from uuid import UUID, uuid4



class DocumentSchema(BaseModel):
    id: str = Field(default_factory=uuid4, description="Unique identifier for the document")
    metadata: dict = Field(default_factory=dict, description="Metadata associated with the document")
    type: str = Field(description="Type of the document, e.g., 'pdf', 'web', etc.")
    source: str = Field(description="Source of the document, e.g., URL or file path")

    @field_validator("metadata", mode="wrap")
    @classmethod
    def validate_metadata(cls, value, handler, info):
        """
        Validate that the metadata contains the required fields.
        Raises ValueError if required fields are missing.
        """
        if not isinstance(value, dict):
            raise ValueError("metadata must be a dict.")
        if not value.get("content"):
            raise ValueError("Document metadata must contain 'content' field.")
        if not isinstance(value.get("content"), str):
            raise ValueError("'content' field in metadata must be a string.")
        return handler(value)