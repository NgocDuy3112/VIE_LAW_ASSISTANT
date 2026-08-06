from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker

from app.api.response import response_router
# from app.api.chat_history import chat_history_router
from app.api.health_check import health_router
from modules.documents.api.v1.ingestion import documents_ingestion_router
from modules.documents.api.v1.retrieve import retrieve_router
from modules.documents.core.init_collection import init_qdrant_collection
# from app.db.async_postgres import AsyncPostgresDatabase



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_qdrant_collection()
    yield


# @asynccontextmanager
# async def old_lifespan(app: FastAPI):
#     try:
#         db = AsyncPostgresDatabase(dbname="chatdb")
#         await db.connect()

#         if not await db.is_connected():
#             raise RuntimeError("PostgreSQL connection failed.")

#         # Step 3: Initialize SQLAlchemy engine and session
#         db_url = db.get_connection_string()
#         engine = create_async_engine(db_url, echo=True, future=True)
#         async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

#         # Store in app state
#         app.state.db = db
#         app.state.engine = engine
#         app.state.postgresql_async_session = async_session_maker

#         yield

#     except Exception as e:
#         print(f"❌ Error during async DB initialization: {e}")
#         raise

#     finally:
#         if hasattr(app.state, "db"):
#             await app.state.db.close()
#             print("🛑 AsyncPostgres DB connection closed.")
#         if hasattr(app.state, "engine"):
#             await app.state.engine.dispose()
#             print("🛑 SQLAlchemy async engine disposed.")




app = FastAPI(lifespan=lifespan, title="Agent Service", version="1.0.0", root_path="/agent-service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(response_router, tags=["Agent Response"])
app.include_router(documents_ingestion_router, prefix="/documents", tags=["Documents"])
app.include_router(retrieve_router, prefix="/documents", tags=["Documents"])
# app.include_router(chat_history_router)
app.include_router(health_router, tags=["Health Check"])



@app.get("/", tags=["Root"])
async def get_status():
    """
    Root endpoint to check the service status.
    """
    return {"message": "Agent Service is running."}