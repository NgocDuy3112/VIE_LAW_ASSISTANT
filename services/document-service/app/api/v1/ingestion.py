from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from qdrant_client import AsyncQdrantClient
import tempfile
import shutil
import os

from app.schemas.ingestion import IngestionRequest, IngestionResponse
from app.core.v1.ingestion import create_ingestion_service, create_ingestion_service_from_documents
from app.dependencies import get_async_qdrant_client  # use the Depends



documents_ingestion_router = APIRouter(prefix="/v1/ingestion")


@documents_ingestion_router.post("", response_model=IngestionResponse, operation_id="index_document")
async def index_document(
    request: IngestionRequest,
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client)
):
    """
    Index a document into Qdrant and return it.
    """
    return await create_ingestion_service(request, async_qdrant_client)


@documents_ingestion_router.post("/pdf", response_model=IngestionResponse, operation_id="index_documents")
async def index_pdf(
    file: UploadFile = File(...),
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client)
):
    """
    Index a PDF file into Qdrant and return the ingested documents.
    """
    if file.content_type != "application/pdf":
        return IngestionResponse(
            status='error',
            detail='Only PDF files are supported'
        )
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_name = file.filename
            # Save the file using its original filename
            tmp_path = os.path.join(tmp_dir, file_name)
            with open(tmp_path, "wb") as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)

            # Pass the path and original filename to your service
            return await create_ingestion_service_from_documents(
                pdf_file=tmp_path,
                async_qdrant_client=async_qdrant_client
            )
    finally:
        file.file.close()