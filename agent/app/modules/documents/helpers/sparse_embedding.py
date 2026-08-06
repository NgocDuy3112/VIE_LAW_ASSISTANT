from sentence_transformers import SparseEncoder

from modules.documents.schemas.document import DocumentSchema
from config import settings



class SparseEmbeddingService():
    def __init__(self, model_name_or_path: str=settings.SPARSE_EMBEDDING_MODEL_PATH, device: str=settings.DEVICE):
        self.sparse_embedding = SparseEncoder(model_name_or_path, device)

    def embed_document(self, document: DocumentSchema) -> dict[str, list]:
        result = self.sparse_embedding.encode_document(document.metadata["content"])
        return {
            "indices": result.coalesce().indices()[0].tolist(),
            "values": result.coalesce().values().tolist()
        }

    def embed_query(self, query: str) -> dict[str, list]:
        result = self.sparse_embedding.encode_query(query)
        return {
            "indices": result.coalesce().indices()[0].tolist(),
            "values": result.coalesce().values().tolist()
        }