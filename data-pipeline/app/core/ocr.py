import logging
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path

logger = logging.getLogger(__name__)


class VietnamesePDFOCR:
    def __init__(self, dpi: int = 300, thread_count: int = 2):
        self.dpi = dpi
        self.thread_count = thread_count

    def extract_text(self, pdf_path: str) -> str:
        logger.info("OCR started: path=%s dpi=%d", pdf_path, self.dpi)
        page_count = int(pdfinfo_from_path(pdf_path)["Pages"])
        texts: list[str] = []
        for page_number in range(1, page_count + 1):
            pages = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt="png",
                first_page=page_number,
                last_page=page_number,
                thread_count=self.thread_count,
            )
            if not pages:
                continue
            text = pytesseract.image_to_string(pages[0], lang="vie", config="--psm 6")
            texts.append(text.strip())
            logger.info("OCR page completed: page=%d/%d chars=%d", page_number, page_count, len(text))
        result = "\n\n".join(text for text in texts if text)
        logger.info("OCR finished: path=%s pages=%d chars=%d", pdf_path, page_count, len(result))
        return result
