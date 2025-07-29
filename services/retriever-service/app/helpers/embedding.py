from sentence_transformers import SentenceTransformer
import numpy as np

from app.schemas.document import DocumentSchema
from app.config import EMBEDDING_MODEL_PATH, EMBEDDING_DIMENSION, DEVICE



class DenseEmbeddingService():
    def __init__(
        self, 
        model_name_or_path: str=EMBEDDING_MODEL_PATH,
        truncate_dim: int=EMBEDDING_DIMENSION, 
        device: str=DEVICE, 
        config_kwargs: dict={"torch_dtype": "float16"}
    ):
        self.embedding = SentenceTransformer(model_name_or_path, truncate_dim, device, config_kwargs)

    def embed_document(self, document: DocumentSchema) -> np.ndarray:
        text = document.metadata["content"]
        embeddings = self.embedding.encode_document(text, show_progress_bar=False)
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        embeddings = self.embedding.encode_query(query, show_progress_bar=False)
        return embeddings