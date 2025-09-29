from fastapi import FastAPI
from app.api import auth as auth_api
from app.core.db import engine, Base
import asyncio


def create_app() -> FastAPI:
    app = FastAPI(title="auth-service")
    app.include_router(auth_api.router)

    @app.on_event("startup")
    async def on_startup():
        # dev: create tables if needed
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app

app = create_app()