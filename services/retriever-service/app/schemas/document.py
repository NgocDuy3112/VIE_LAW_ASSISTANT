from pydantic import BaseModel, Field, field_validator
from uuid import uuid4



class DocumentSchema(BaseModel):
    id: str = Field(default_factory=uuid4, description="Unique identifier for the document")
    metadata: dict = Field(default_factory=dict, description="Metadata associated with the document")

    @field_validator("metadata", mode="wrap")
    @classmethod
    def validate_metadata(cls, metadata: dict) -> dict:
        """
        Validate that the metadata contains the required fields.
        Raises ValueError if required fields are missing.
        """
        if not metadata.get("content"):
            raise ValueError("Document metadata must contain 'content' field.")
        if not isinstance(metadata.get("content"), str):
            raise ValueError("'content' field in metadata must be a string.")
        # Add more validation rules as needed
        return metadata