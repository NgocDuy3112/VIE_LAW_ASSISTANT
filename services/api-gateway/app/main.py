from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.chat_completions import chat_completions_router
from app.api.v1.ingestion import ingestion_router
from app.api.v1.retrive import retrieve_router
from app.api.health_check import health_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_completions_router, tags=["Chat Completions endpoint"])
app.include_router(retrieve_router, tags=["Retrieving endpoint"])
app.include_router(ingestion_router, tags=["Ingestion endpoint"])
app.include_router(health_router, tags=["Health check"])



@app.get("/", tags=["Root"])
async def get_status():
    """
    Root endpoint to check the service status.
    """
    return {"message": "API Gateway is running."}