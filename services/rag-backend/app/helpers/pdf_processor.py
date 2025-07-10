import pymupdf4llm
from app.schemas.document import DocumentSchema
from langchain_text_splitters import CharacterTextSplitter



class PDFProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.text_splitter = CharacterTextSplitter(separator='**')

    def extract_documents(self) -> list[DocumentSchema]:
        documents = []
        md_text = pymupdf4llm.to_markdown(self.file_path)
        langchain_documents = self.text_splitter.split_documents([md_text])
        for langchain_doc in langchain_documents:
            document = DocumentSchema()
            document.metadata["content"] = langchain_doc.page_content
            document.metadata["file_path"] = self.file_path
            documents.append(document)
        return documents