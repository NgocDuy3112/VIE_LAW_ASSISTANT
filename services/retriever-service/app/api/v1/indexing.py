from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from qdrant_client import AsyncQdrantClient
import tempfile
import shutil

from app.schemas.document import DocumentSchema
from app.core.v1.indexing import create_indexing_service, create_indexing_service_from_pdf
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
    return await create_indexing_service(document, async_qdrant_client)


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
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        documents = await create_indexing_service_from_pdf(tmp_path, async_qdrant_client)
        return documents
    finally:
        file.file.close()