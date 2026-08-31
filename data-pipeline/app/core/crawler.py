from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

import os
import logging
from datetime import datetime

from app.config import settings
from app.schemas.crawler import PDFItem, CrawlerRequest, CrawlerResponse
from app.core.downloader import PDFDownloader
from app.core.indexer import PDFIndexer

logger = logging.getLogger(__name__)


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    service = ChromeService(executable_path=os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
    driver = webdriver.Chrome(service=service, options=options)
    return driver


class LegalDocumentCrawler:
    def __init__(
        self, 
        driver: webdriver.Chrome | None=None, 
        limit: int | None=settings.LIMIT, 
        url: str=settings.LEGAL_LAW_URL, 
        timeout: int=settings.TIMEOUT
    ):
        self.driver = driver if driver else create_driver()
        self.wait = WebDriverWait(self.driver, timeout)
        self.url = url
        self.limit = limit
        self.downloader = PDFDownloader()


    async def crawl_pdf(
        self,
        request: CrawlerRequest
    ):
        try:
            self.driver.get(self.url)

            # Select filters
            if request.category:
                category_input_section = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocCategory']"))
                )
                Select(category_input_section).select_by_visible_text(request.category)

            if request.organization:
                organization_input_section = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocOrg']"))
                )
                Select(organization_input_section).select_by_visible_text(request.organization)

            if request.doc_year:
                doc_year_input_section = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocYear']"))
                )
                Select(doc_year_input_section).select_by_visible_text(str(request.doc_year))

            if request.keyword:
                enter_text = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][maxlength='100']"))
                )
                enter_text.clear()
                enter_text.send_keys(request.keyword)

            # Submit search
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            )
            submit_button.click()

            # Wait until results are loaded
            self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "bl-doc-file"))
            )

            results = []
            logger.info("Crawler results loaded: url=%s", self.url)

            # Get counts dynamically each time to avoid stale elements
            issue_dates_count = len(self.driver.find_elements(By.CSS_SELECTOR, "span[class='issued-date']"))
            titles_count = len(self.driver.find_elements(By.CSS_SELECTOR, "span[class='substract']"))
            sections_count = len(self.driver.find_elements(By.CLASS_NAME, "bl-doc-file"))

            for i in range(min(self.limit, titles_count, sections_count, issue_dates_count)):
                # Re-locate every time to avoid stale references
                title_text = self.driver.find_elements(By.CSS_SELECTOR, "span[class='substract']")[i].text.strip()
                date_text = self.driver.find_elements(By.CSS_SELECTOR, "span[class='issued-date']")[i].text.strip()
                pdf_url = self.driver.find_elements(By.CLASS_NAME, "bl-doc-file")[i]\
                    .find_element(By.TAG_NAME, "a")\
                    .get_attribute("href")

                try:
                    issued_date = datetime.strptime(date_text, "%d/%m/%Y").date()
                except ValueError:
                    continue

                results.append(PDFItem(
                    title=title_text,
                    url=pdf_url,
                    issued_date=issued_date
                ))

            logger.info("Starting download/index pipeline: documents=%d", len(results))
            indexer = PDFIndexer()
            downloaded = []
            for item in results:
                local_path, error = await self.downloader.download(item.title, item.url)
                indexed = 0
                index_error = None
                if local_path:
                    try:
                        indexed = await indexer.index_pdf(local_path)
                    except Exception as exc:
                        logger.exception("PDF indexing failed: path=%s", local_path)
                        index_error = str(exc)
                downloaded.append(item.model_copy(update={
                    "local_path": local_path,
                    "downloaded": local_path is not None,
                    "download_error": error or index_error,
                }))

            await indexer.close()
            success_count = sum(item.downloaded for item in downloaded)
            logger.info("Crawl pipeline finished: downloaded=%d total=%d", success_count, len(downloaded))
            return CrawlerResponse(
                status="success",
                count=len(downloaded),
                data=downloaded,
                detail=f"Crawled {len(downloaded)} documents; downloaded {success_count}."
            )

        except Exception as e:
            return CrawlerResponse(
                status="error",
                count=0,
                data=[],
                detail=str(e)
            )