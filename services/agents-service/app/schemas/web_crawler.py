from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from pydantic import BaseModel, Field


class WebCrawlerToolInputSchema(BaseIOSchema):
    keyword: str | None = Field(default=None, description="Search keyword")
    category: str | None = Field(default=None, description="Document category name")
    organization: str | None = Field(default=None, description="Document organization name")
    doc_year: int | None = Field(default=None, description="Year of the document")


class PDFItem(BaseModel):
    title: str
    url: str


class WebCrawlerToolOutputSchema(BaseIOSchema):
    data: list[PDFItem] = Field(description="List of PDF results")