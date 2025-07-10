from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat_completions import chat_completions_router
from app.api.health_check import health_router



app = FastAPI(title="LLM Service", version="1.0.0", root_path="/llm-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_completions_router)
app.include_router(health_router, tags=["Health Check"])



@app.get("/", tags=["Root"])
async def get_status():
    """
    Root endpoint to check the service status.
    """
    return {"message": "LLM Service is running."}