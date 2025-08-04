import hashlib
from markitdown import MarkItDown
from app.schemas.document import DocumentSchema
from app.helpers.text_splitter import CharacterTextSplitter


def calculate_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class DocumentsProcessor:
    def __init__(self, seperstor: str='**', enable_plugins:bool=True):
        self.text_splitter = CharacterTextSplitter(separator=seperstor)
        self.markitdown = MarkItDown(enable_plugins=enable_plugins)

    def extract_documents(self, file_path: str) -> list[DocumentSchema]:
        documents = []
        md_text = self.markitdown.convert(file_path).text_content
        paragraphs = self.text_splitter.split_text(md_text)
        for paragraph in paragraphs:
            document = DocumentSchema()
            document.metadata["id"] = document.id
            document.metadata["content"] = paragraph
            document.metadata["content_hash"] = calculate_content_hash(paragraph)
            document.metadata["source"] = file_path
            document.metadata["type"] = "pdf"
            documents.append(document)
        return documents