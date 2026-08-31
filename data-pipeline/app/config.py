from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

load_dotenv("/src/configs/.env", override=True)


class Settings(BaseSettings):
    LEGAL_LAW_URL: str
    TIMEOUT: int
    LIMIT: int
    PDF_DOWNLOAD_DIR: str
    DOWNLOAD_TIMEOUT: int
    ELASTICSEARCH_URL: str
    ELASTICSEARCH_INDEX: str
    EMBEDDING_URL: str
    EMBEDDING_DIMENSION: int
    EMBEDDING_MODEL: str

    model_config = ConfigDict(extra="ignore")


settings = Settings()
