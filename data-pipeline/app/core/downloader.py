import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class PDFDownloader:
    def __init__(self, output_dir: str = settings.PDF_DOWNLOAD_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _filename(self, title: str, url: str) -> str:
        safe_title = re.sub(r"[^\w\-. ]", "", title, flags=re.UNICODE).strip()
        safe_title = re.sub(r"\s+", "_", safe_title)[:150] or "document"
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
        return f"{safe_title}_{url_hash}.pdf"

    async def download(self, title: str, url: str) -> tuple[str | None, str | None]:
        destination = self.output_dir / self._filename(title, url)
        if destination.exists() and destination.stat().st_size > 0:
            logger.info("PDF already exists: %s", destination)
            return str(destination), None

        timeout = aiohttp.ClientTimeout(total=settings.DOWNLOAD_TIMEOUT)
        try:
            logger.info("Downloading PDF: title=%s url=%s", title, url)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as response:
                    response.raise_for_status()
                    content_type = response.headers.get("Content-Type", "").lower()
                    if "pdf" not in content_type and not urlparse(str(response.url)).path.lower().endswith(".pdf"):
                        return None, f"Unexpected content type: {content_type or 'unknown'}"
                    data = await response.read()

            if not data.startswith(b"%PDF"):
                return None, "Downloaded content is not a valid PDF"
            destination.write_bytes(data)
            logger.info("PDF downloaded: path=%s bytes=%d", destination, len(data))
            return str(destination), None
        except Exception as exc:
            logger.exception("PDF download failed: url=%s", url)
            return None, str(exc)
