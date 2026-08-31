import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

from app.core.crawler import LegalDocumentCrawler
from app.schemas.crawler import CrawlerRequest

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Ho_Chi_Minh"))


async def daily_crawl_job() -> None:
    crawler = LegalDocumentCrawler()
    try:
        result = await crawler.crawl_pdf(CrawlerRequest())
        logger.info("Daily crawl finished: status=%s count=%s", result.status, result.count)
    except Exception:
        logger.exception("Daily crawl failed")
    finally:
        crawler.driver.quit()


def start_scheduler() -> None:
    scheduler.add_job(
        daily_crawl_job,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_legal_crawl",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("Daily crawler scheduled for 09:00 Asia/Ho_Chi_Minh")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
