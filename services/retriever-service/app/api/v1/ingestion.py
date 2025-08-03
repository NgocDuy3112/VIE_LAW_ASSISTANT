from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from qdrant_client import AsyncQdrantClient
import tempfile
import shutil
import os

from app.schemas.document import DocumentSchema
from app.core.v1.ingestion import create_ingestion_service, create_ingestion_service_from_pdf
from app.dependencies import get_async_qdrant_client  # use the Depends



indexing_router = APIRouter(prefix="/v1/index")


@indexing_router.post("/", response_model=DocumentSchema)
async def index_document(
    document: DocumentSchema,
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client)
):
    """
    Index a document into Qdrant and return it.
    """
    return await create_ingestion_service(document, async_qdrant_client)


@indexing_router.post("/pdf", response_model=list[DocumentSchema])
async def index_pdf(
    file: UploadFile = File(...),
    async_qdrant_client: AsyncQdrantClient = Depends(get_async_qdrant_client)
):
    """
    Index a PDF file into Qdrant and return the indexed documents.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_name = file.filename
            # Save the file using its original filename
            tmp_path = os.path.join(tmp_dir, file_name)
            with open(tmp_path, "wb") as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)

            # Pass the path and original filename to your service
            documents = await create_ingestion_service_from_pdf(
                pdf_file=tmp_path,
                async_qdrant_client=async_qdrant_client
            )
            for document in documents:
                document.metadata["source"] = file_name
            return documents

    finally:
        file.file.close()