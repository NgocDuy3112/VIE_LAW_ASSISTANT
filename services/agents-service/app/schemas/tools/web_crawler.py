from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from pydantic import Field

from app.schemas.pdf_item import PDFItem


class WebCrawlerToolInputSchema(BaseIOSchema):
    """
        The input schema for the tool
    """
    keyword: str | None = Field(default=None, description="Search keyword")
    category: str | None = Field(default=None, description="Document category name")
    organization: str | None = Field(default=None, description="Document organization name")
    doc_year: int | None = Field(default=None, description="Year of the document")


class WebCrawlerToolOutputSchema(BaseIOSchema):
    """
        The output schema for the tool
    """
    status: str = Field(description="Status of the operation, e.g., success or error")
    count: int = Field(description="Number of PDFs returned")
    data: list[PDFItem] = Field(description="List of PDF results")
    message: str | None = Field(default=None, description="Error message if status is error")