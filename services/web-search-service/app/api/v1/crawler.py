from fastapi import APIRouter, Query
from app.core.crawler import *


crawler_router = APIRouter(prefix="/v1")


@crawler_router.get("/", response_model=GetPDFsResponse)
def get_pdfs(
    keyword: str | None = Query(None, description="Search keyword"),
    category: str | None = Query(None, description="Document category"),
    organization: str | None = Query(None, description="Organization name"),
    doc_year: int | None = Query(None, description="Document year"),
):
    driver = create_driver()
    try:
        crawler = LegalDocumentCrawler(driver)
        result = crawler.crawl_pdf(
            keyword=keyword,
            category=category,
            organization=organization,
            doc_year=doc_year
        )
    except Exception as e:
        result = GetPDFsResponse(status="error", count=0, data=[], message=str(e))
    finally:
        driver.quit()
    return result