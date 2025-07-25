from sentence_transformers import SentenceTransformer
import numpy as np

from app.schemas.document import DocumentSchema
from app.config import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION, DEVICE


embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME, 
    truncate_dim=EMBEDDING_DIMENSION, 
    device=DEVICE,
    config_kwargs={"torch_dtype": "float16"}  # Use float16 for memory efficiency
)


def embed_document(
    document: DocumentSchema,
    embedding_model: SentenceTransformer=embedding_model
) -> np.ndarray:
    """
    Embed a document using the configured embedding model.

    Args:
        document (Document): The document to embed.

    Returns:
        np.ndarray: The embeddings for the document.
    """
    text = document.metadata["content"]
    embeddings = embedding_model.encode(text, convert_to_numpy=True, show_progress_bar=False)
    return embeddings



def embed_query(
    query: str, 
    embedding_model: SentenceTransformer=embedding_model
) -> np.ndarray:
    embeddings = embedding_model.encode(query, convert_to_numpy=True, show_progress_bar=False)
    return embeddings