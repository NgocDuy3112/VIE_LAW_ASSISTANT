from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os



load_dotenv("/src/configs/.env", override=True)


class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    BASE_URL: str = os.getenv("BASE_URL")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    LEGAL_LAW_URL: str = os.getenv("LEGAL_LAW_URL", 'https://vanban.chinhphu.vn/he-thong-van-ban')
    TIMEOUT: int = int(os.getenv("TIMEOUT", 300))
    LIMIT: int = int(os.getenv("LIMIT", 3))
    WEB_CRAWLER_URL: str = os.getenv("WEB_CRAWLER_URL")


settings = Settings()