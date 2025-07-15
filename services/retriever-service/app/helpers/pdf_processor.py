import hashlib
import pymupdf4llm
from app.schemas.document import DocumentSchema
from helpers.text_splitter import CharacterTextSplitter


def calculate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class PDFProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.text_splitter = CharacterTextSplitter(separator='**')

    def extract_documents(self) -> list[DocumentSchema]:
        documents = []
        md_text = pymupdf4llm.to_markdown(self.file_path)
        paragraphs = self.text_splitter.split_text(md_text)
        for paragraph in paragraphs:
            document = DocumentSchema()
            document.metadata["id"] = str(document.id)
            document.metadata["content"] = paragraph
            document.metadata["content_hash"] = calculate_content_hash(paragraph)
            document.metadata["file_path"] = self.file_path
            documents.append(document)
        return documents