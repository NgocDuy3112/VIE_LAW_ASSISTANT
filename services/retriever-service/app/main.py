from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.ask import ask_router
from app.api.v1.indexing import indexing_router
from app.api.v1.retriever import retriever_router
from app.api.health_check import health_router



app = FastAPI(title="Retriever Service", version="1.0.0", root_path="/retriever-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(ask_router)
app.include_router(indexing_router)
app.include_router(retriever_router)
app.include_router(health_router, tags=["Health Check"])



@app.get("/", tags=["Root"])
async def get_status():
    """
    Root endpoint to check the service status.
    """
    return {"message": "Retriever Service is running."}