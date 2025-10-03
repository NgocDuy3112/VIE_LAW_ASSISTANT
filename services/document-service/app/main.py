from fastmcp import FastMCP

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.init_collection import init_qdrant_collection
from app.api.v1.ingestion import documents_ingestion_router
from app.api.v1.retrieve import retrieve_router
from app.api.health_check import health_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_qdrant_collection()
    yield



main_app = FastAPI(lifespan=lifespan, title="Retriever Service", version="1.0.0", root_path="/retriever-service")
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
main_app.include_router(documents_ingestion_router, tags=["Documents Ingestion endpoint"])
main_app.include_router(retrieve_router, tags=["Retrieving endpoint"])
main_app.include_router(health_router, tags=["Health Check"])



@main_app.get("/", tags=["Root"])
async def get_status():
    """
    Root endpoint to check the service status.
    """
    return {"message": "Retriever Service is running."}



mcp = FastMCP.from_fastapi(app=main_app, name="Document MCP")
mcp_app = mcp.http_app(path='/mcp')



app = FastAPI(
    title="Document service API with MCP",
    routes=[
        *main_app.routes,
        *mcp_app.routes
    ],
    lifespan=mcp_app.lifespan
)