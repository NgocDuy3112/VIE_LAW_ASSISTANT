from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

import requests
import asyncio
import aiohttp

from config import LEGAL_LAW_URL


class LegalDocumentCrawler:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    service = ChromeService(ChromeDriverManager().install())
    
    def __init__(self, timeout=30):
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.wait = WebDriverWait(self.driver, timeout)
        self.url = LEGAL_LAW_URL


    async def crawl_pdf(
        self, 
        output_dir: str,
        keyword: str | None = None,
        category: str | None = None, 
        organization: str | None = None, 
        doc_year: int | None = None,
    ):
        # Run Selenium (blocking) calls in a thread
        await asyncio.to_thread(self.driver.get, self.url)

        if category is not None:
            category_input_section = await asyncio.to_thread(
                self.wait.until,
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocCategory']"))
            )
            await asyncio.to_thread(Select(category_input_section).select_by_visible_text, category)

        if organization is not None:
            organization_input_section = await asyncio.to_thread(
                self.wait.until,
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocOrg']"))
            )
            await asyncio.to_thread(Select(organization_input_section).select_by_visible_text, organization)

        if doc_year is not None:
            doc_year_input_section = await asyncio.to_thread(
                self.wait.until,
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name*='DocYear']"))
            )
            await asyncio.to_thread(Select(doc_year_input_section).select_by_visible_text, str(doc_year))

        if keyword is not None:
            enter_text = await asyncio.to_thread(
                self.wait.until,
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][maxlength='100']"))
            )
            await asyncio.to_thread(enter_text.clear)
            await asyncio.to_thread(enter_text.send_keys, keyword)

        submit_button = await asyncio.to_thread(
            self.wait.until,
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        await asyncio.to_thread(submit_button.click)

        pdf_section = await asyncio.to_thread(
            self.wait.until,
            EC.presence_of_element_located((By.CLASS_NAME, "bl-doc-file"))
        )
        pdf_url = await asyncio.to_thread(
            pdf_section.find_element(By.TAG_NAME, "a").get_attribute, "href"
        )

        # Async download PDF
        pdf_path = f"{output_dir}/{pdf_url.split('/')[-1]}" if output_dir else pdf_url
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                content = await response.read()
                with open(pdf_path, "wb") as f:
                    f.write(content)