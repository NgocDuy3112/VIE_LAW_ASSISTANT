from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

import os
from datetime import datetime

from app.config import *
from app.schemas.response import *


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
    def __init__(self, driver: webdriver.Chrome | None = None, limit: int | None = LIMIT, url: str = LEGAL_LAW_URL, timeout: int=TIMEOUT):
        self.driver = driver if driver else create_driver()
        self.wait = WebDriverWait(self.driver, timeout)
        self.url = url
        self.limit = limit


    def crawl_pdf(
        self,
        keyword: str | None = None,
        category: str | None = None, 
        organization: str | None = None, 
        doc_year: int | None = None,
    ):
        try:
            self.driver.get(self.url)

            # Select filters
            if category:
                category_input_section = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocCategory']"))
                )
                Select(category_input_section).select_by_visible_text(category)

            if organization:
                organization_input_section = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocOrg']"))
                )
                Select(organization_input_section).select_by_visible_text(organization)

            if doc_year:
                doc_year_input_section = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocYear']"))
                )
                Select(doc_year_input_section).select_by_visible_text(str(doc_year))

            if keyword:
                enter_text = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][maxlength='100']"))
                )
                enter_text.clear()
                enter_text.send_keys(keyword)

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

            return GetPDFsResponse(
                status="success",
                count=len(results),
                data=results,
                message="Documents crawled successfully!"
            )

        except Exception as e:
            return GetPDFsResponse(
                status="error",
                count=0,
                data=[],
                message=str(e)
            )