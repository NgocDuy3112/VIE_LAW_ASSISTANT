from pydantic import BaseSettings


class Settings(BaseSettings):
    # Use a strong secret in production
    AUTH_HS256_SECRET: str = "change-me-in-production"

    # Lifetimes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Async DB URL. Example:
    # postgresql+asyncpg://user:pass@localhost:5432/auth_db
    # For dev: sqlite+aiosqlite:///./auth.db
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/auth_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()