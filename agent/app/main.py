from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.response import response_router
from app.api.rate_limit import setup_rate_limit
from app.api.health_check import health_router
from app.api.sessions import sessions_router
from modules.documents.core.init_collection import init_elasticsearch_index
from db.engine import engine
from db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Init Elasticsearch
    await init_elasticsearch_index()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan, title="Agent Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(response_router, tags=["Agent Response"])
app.include_router(sessions_router)
app.include_router(health_router, tags=["Health Check"])
setup_rate_limit(app)


@app.get("/", tags=["Root"])
async def get_status():
    return {"message": "Agent Service is running."}
