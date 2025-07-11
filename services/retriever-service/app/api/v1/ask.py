from fastapi import APIRouter, Depends
from qdrant_client import AsyncQdrantClient
from app.helpers.caching import ValkeySemanticCache
from app.schemas.ask import AskRequest
from app.schemas.retrieve import RetrieveRequest