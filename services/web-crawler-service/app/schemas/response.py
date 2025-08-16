from pydantic import BaseModel, Field



class PDFItem(BaseModel):
    title: str
    url: str


class GetPDFsResponse(BaseModel):
    status: str = Field(description="Status of the operation, e.g., success or error")
    count: int = Field(description="Number of PDFs returned")
    data: list[PDFItem] = Field(description="List of PDF results")
    message: str | None = Field(default=None, description="Error message if status is error")