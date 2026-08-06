from typing import Literal
from pydantic import BaseModel, Field



class PDFItem(BaseModel):
    title: str
    url: str



class CrawlerRequest(BaseModel):
    keyword: str | None = Field(default=None, description="Search keyword")
    category: str | None = Field(default=None, description="Document category name")
    organization: str | None = Field(default=None, description="Document organization name")
    doc_year: int | None = Field(default=None, description="Year of the document")



class CrawlerResponse(BaseModel):
    status: Literal['success', 'error']
    count: int = Field(description="Number of PDFs returned")
    data: list[PDFItem] = Field(description="List of PDF results")
    detail: str | None = Field(default=None, description="Error message if status is error")