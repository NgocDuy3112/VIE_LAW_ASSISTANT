# from sentence_transformers import SentenceTransformer
# import numpy as np
# from app.config import EMBEDDING_MODEL_PATH, EMBEDDING_DIMENSION, DEVICE



# embedding_model = SentenceTransformer(
#     EMBEDDING_MODEL_PATH, 
#     truncate_dim=EMBEDDING_DIMENSION, 
#     device=DEVICE,
#     config_kwargs={"torch_dtype": "float16"}  # Use float16 for memory efficiency
# )


# def embed_query(
#     query: str, 
#     embedding_model: SentenceTransformer=embedding_model
# ) -> np.ndarray:
#     embeddings = embedding_model.encode(query, convert_to_numpy=True, show_progress_bar=False)
#     return embeddings