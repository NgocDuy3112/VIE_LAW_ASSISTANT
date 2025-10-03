from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL")
    LM_STUDIO_BASE_URL: str = os.getenv("LM_STUDIO_BASE_URL")

    NUM_REQUESTS_PER_MINUTE: int = int(os.getenv("NUM_REQUESTS_PER_MINUTE", 10))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 60))
    RATE_LIMIT_URI: str = os.getenv("RATE_LIMIT_URI")
    POSTGRES_CHECKPOINTS_URI: str = os.getenv("POSTGRES_CHECKPOINTS_URI")


settings = Settings()