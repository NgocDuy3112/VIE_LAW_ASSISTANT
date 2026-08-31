from typing import Literal
from pydantic import BaseModel, Field
from modules.documents.schemas.document import DocumentSchema



class RetrieveRequest(BaseModel):
    query: str = Field(description="The user's query")
    top_k: int = Field(description="Maximum number of documents to retrieve", default=5)
    filter: dict | None = Field(description="Optional Elasticsearch filter", default=None)



class RetrieveResponse(BaseModel):
    results: list[DocumentSchema]
    status: Literal["success", "error"]
    detail: str | None