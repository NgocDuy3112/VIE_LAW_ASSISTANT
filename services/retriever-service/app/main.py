from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.ask import ask_router
from app.api.v1.indexing import indexing_router
from app.api.v1.retriever import retriever_router



