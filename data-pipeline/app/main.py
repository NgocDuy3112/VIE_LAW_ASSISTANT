from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.crawler import crawler_router
from app.api.health_check import health_router
from app.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting data pipeline service")
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Data Pipeline", version="1.0.0", lifespan=lifespan, root_path="/web-search-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(crawler_router)
app.include_router(health_router, tags=["Health Check"])


@app.get("/", tags=["Root"])
async def get_status():
    return {"message": "Data Pipeline is running."}
