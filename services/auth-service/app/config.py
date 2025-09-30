from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os


load_dotenv(dotenv_path="/src/configs/.env", override=True)



class Settings(BaseSettings):
    AUTH_HS256_SECRET: str = os.getenv("AUTH_HS256_SECRET")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    AUTH_ISSUER: str = os.getenv("AUTH_ISSUER")
    AUTH_AUDIENCE: str = os.getenv("AUTH_AUDIENCE")
    DATABASE_URL: str = os.getenv("DATABASE_URL")


settings = Settings()