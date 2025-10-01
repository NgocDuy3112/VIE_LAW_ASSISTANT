from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv("/src/configs/.env", override=True)


class Settings(BaseSettings):
    BASE_URL: str = os.getenv("BASE_URL")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    NUM_REQUESTS_PER_MINUTE: int = int(os.getenv("NUM_REQUESTS_PER_MINUTE", 10))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 60))
    RATE_LIMIT_URI: str = os.getenv("RATE_LIMIT_URI")


settings = Settings()