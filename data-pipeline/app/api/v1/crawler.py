from fastapi import APIRouter

from app.schemas.crawler import CrawlerRequest, CrawlerResponse
from app.core.crawler import LegalDocumentCrawler

crawler_router = APIRouter(prefix="/v1")


@crawler_router.get("/crawl", response_model=CrawlerResponse)
async def crawl_pdfs(request: CrawlerRequest):
    crawler = LegalDocumentCrawler()
    try:
        return await crawler.crawl_pdf(request)
    finally:
        crawler.driver.quit()
