from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

import instructor
import openai
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

from app.schemas.web_crawler import WebCrawlerToolInputSchema, WebCrawlerToolOutputSchema
from app.config import *



class WebCrawlerToolConfig(BaseToolConfig):
    web_url: str = Field(default=LEGAL_LAW_URL, description="The website URL to be crawled")
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
        self.web_url = config.web_url
        self.limit = config.limit
        self.timeout = config.timeout

    async def arun(self, params: WebCrawlerToolInputSchema) -> WebCrawlerToolOutputSchema:
        pass
    
    def run(self, params: WebCrawlerToolInputSchema) -> WebCrawlerToolOutputSchema:
        raise NotImplementedError()