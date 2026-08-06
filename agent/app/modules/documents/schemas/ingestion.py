from typing import Literal
from pydantic import BaseModel
from qdrant_client.models import Filter

from schemas.document import DocumentSchema



class IngestionRequest(BaseModel):
    document: DocumentSchema



class IngestionResponse(BaseModel):
    status: Literal['success', 'error']
    detail: str | None