from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

load_dotenv("/src/configs/.env", override=True)


class Settings(BaseSettings):
    # LLM
    LLM_BASE_URL: str
    LLM_MODEL: str

    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # PostgreSQL Agent
    POSTGRES_AGENT_USER: str
    POSTGRES_AGENT_PASSWORD: str
    POSTGRES_AGENT_DB: str
    POSTGRES_AGENT_URL: str

    # Elasticsearch
    ELASTICSEARCH_URL: str
    ELASTICSEARCH_INDEX: str

    # Embedding
    EMBEDDING_URL: str
    EMBEDDING_DIMENSION: int

    # Redis
    RATE_LIMIT_URI: str

    # App
    NUM_REQUESTS_PER_MINUTE: int
    REQUEST_TIMEOUT_SECONDS: int

    model_config = ConfigDict(extra="ignore")


settings = Settings()
