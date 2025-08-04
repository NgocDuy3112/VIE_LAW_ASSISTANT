from pydantic import BaseModel
from qdrant_client.models import Filter



class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 3
    filter: Filter | None = None