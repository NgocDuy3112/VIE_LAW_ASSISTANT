from pydantic import Field
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig

import aiohttp
import asyncio

from app.schemas.tools.web_crawler import WebCrawlerToolInputSchema, WebCrawlerToolOutputSchema
from app.config import *



class WebCrawlerToolConfig(BaseToolConfig):
    limit: int = Field(default=LIMIT, description="The maximum PDF documents to be crawled")
    timeout: int = Field(default=TIMEOUT, description="The timeout of the crawler")



class WebCrawlerTool(BaseTool[WebCrawlerToolInputSchema, WebCrawlerToolOutputSchema]):
    """Tool for performing the crawling operation.

    Args:
        input_schema (WebCrawlerToolInputSchema): The schema for the input data.
        output_schema (WebCrawlerToolOutputSchema): The schema for the output data.
        web_url (str): The URL of the website to be crawled
    """
    def __init__(self, config: WebCrawlerToolConfig = WebCrawlerToolConfig()):
        super().__init__(config)
        self.limit = config.limit
        self.timeout = config.timeout
    
    def run(self, params: WebCrawlerToolInputSchema) -> WebCrawlerToolOutputSchema:
        return asyncio.run(self._async_run(params))
    
    async def _async_run(self, params: WebCrawlerToolInputSchema) -> WebCrawlerToolOutputSchema:
        payload = params.model_dump()
        payload.update({
            "limit": self.limit,
            "timeout": self.timeout
        })

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(WEB_CRAWLER_SERVICE_URL, json=payload) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Crawler service error {resp.status}: {await resp.text()}")
                resp_json = await resp.json()
                return WebCrawlerToolOutputSchema(**resp_json)