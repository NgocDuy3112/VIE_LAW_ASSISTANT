from pydantic import BaseModel, Field



class GetPDFsRequest(BaseModel):
    limit: int = Field(default=3, ge=1, le=5, description="Max number of PDFs to return")
    keyword: str | None = Field(default=None, description="Search keyword")
    category: str | None = Field(default=None, description="Document category name")
    organization: str | None = Field(default=None, description="Document organization name")
    doc_year: int | None = Field(default=None, description="Year of the document")