from pydantic import BaseModel, Field


class PDFItem(BaseModel):
    title: str = Field(..., description="The title of the PDF")
    url: str = Field(..., description="The URL of the PDF")