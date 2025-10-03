from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


class Settings(BaseSettings):
    QDRANT_CLIENT_URL: str = os.getenv("QDRANT_CLIENT_URL")
    SEMANTIC_CACHE_VALKEY_URL: str = os.getenv("SEMANTIC_CACHE_VALKEY_URL")
    POSTGRES_CHECKPOINTS_URI: str = os.getenv("POSTGRES_CHECKPOINTS_URI")

    RATE_LIMIT_URI: str = os.getenv("RATE_LIMIT_URI")

    EMBEDDING_MODEL_PATH: str = os.getenv("EMBEDDING_MODEL_PATH")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION"))
    DEVICE: str = os.getenv("DEVICE", "cpu")

    SPARSE_EMBEDDING_MODEL_PATH: str = os.getenv("SPARSE_EMBEDDING_MODEL_PATH")

    NUM_REQUESTS_PER_MINUTE: int = int(os.getenv("NUM_REQUESTS_PER_MINUTE"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS"))


settings = Settings()