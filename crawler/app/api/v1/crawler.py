from fastapi import APIRouter

from app.schemas.crawler import CrawlerRequest, CrawlerResponse
from app.core.crawler import *



crawler_router = APIRouter(prefix="/v1")



@crawler_router.get("/crawl", response_model=CrawlerResponse)
async def crawl_pdfs(request: CrawlerRequest):
    crawler = LegalDocumentCrawler()
    return await crawler.crawl_pdf(
        keyword=request.keyword,
        category=request.category,
        organization=request.organization,
        doc_year=request.doc_year
    )