from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


QDRANT_CLIENT_URL = os.getenv("QDRANT_CLIENT_URL")
SEMANTIC_CACHE_VALKEY_URL = os.getenv("SEMANTIC_CACHE_VALKEY_URL", "valkey://localhost:6380/0")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION"))
DEVICE = os.getenv("DEVICE", "cpu")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
RATE_LIMIT_URI = os.getenv("RATE_LIMIT_URI")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8001")