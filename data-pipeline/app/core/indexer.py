import asyncio
import hashlib
import aiohttp
from elasticsearch import AsyncElasticsearch
from markitdown import MarkItDown

from app.config import settings
from app.core.ocr import VietnamesePDFOCR
from app.core.text_splitter import LegalTextSplitter
import logging

logger = logging.getLogger(__name__)


class PDFIndexer:
    def __init__(self):
        self.client = AsyncElasticsearch(settings.ELASTICSEARCH_URL)
        self.embedding_url = settings.EMBEDDING_URL
        self.markitdown = MarkItDown(enable_plugins=True)

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        url = self.embedding_url.rstrip("/") + "/v1/embeddings"
        payload = {"input": texts, "model": settings.EMBEDDING_MODEL}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                response.raise_for_status()
                data = await response.json()
                return [item["embedding"] for item in data["data"]]

    async def ensure_index(self) -> None:
        if not await self.client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
            await self.client.indices.create(
                index=settings.ELASTICSEARCH_INDEX,
                mappings={"properties": {
                    "content": {"type": "text"},
                    "content_hash": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "type": {"type": "keyword"},
                    "content_vector": {"type": "dense_vector", "dims": settings.EMBEDDING_DIMENSION, "index": True, "similarity": "cosine"},
                }},
            )

    async def index_pdf(self, file_path: str) -> int:
        await self.ensure_index()
        logger.info("Extracting PDF text: path=%s", file_path)
        try:
            text = self.markitdown.convert(file_path).text_content or ""
        except Exception:
            logger.exception("Text extraction failed; falling back to OCR")
            text = ""
        if not text.strip():
            logger.info("No text layer found; falling back to Vietnamese Tesseract OCR")
            text = await asyncio.to_thread(VietnamesePDFOCR().extract_text, file_path)
        chunks = LegalTextSplitter().split(text)
        logger.info("PDF extracted: path=%s chunks=%d", file_path, len(chunks))

        # Embed all chunks in batch
        texts_to_embed = [chunk.strip() for chunk in chunks if chunk.strip()]
        vectors = await self._embed(texts_to_embed)
        logger.info("Embedded %d chunks", len(vectors))

        indexed = 0
        for chunk_number, (chunk, vector) in enumerate(zip(texts_to_embed, vectors), start=1):
            content_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            exists = await self.client.count(index=settings.ELASTICSEARCH_INDEX, query={"term": {"content_hash": content_hash}})
            if exists["count"]:
                logger.info("Chunk already indexed: chunk=%d hash=%s", chunk_number, content_hash)
                continue
            await self.client.index(index=settings.ELASTICSEARCH_INDEX, document={"content": chunk, "content_hash": content_hash, "source": file_path, "type": "pdf", "content_vector": vector}, refresh="wait_for")
            indexed += 1
            logger.info("Chunk indexed: chunk=%d/%d hash=%s", chunk_number, len(texts_to_embed), content_hash)
        logger.info("PDF indexing finished: path=%s indexed=%d", file_path, indexed)
        return indexed

    async def close(self) -> None:
        await self.client.close()
