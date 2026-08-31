from typing import Literal
import aiohttp

from config import settings

ChatMessage = dict[str, str]


class ChatModel:
    def __init__(self, model_name: str, temperature: float = 0.1):
        self.provider, self.model = model_name.split("/", 1)
        self.temperature = temperature

    async def complete(self, messages: list[ChatMessage]) -> str:
        return await self.response(messages)

    async def route(self, messages: list[ChatMessage]) -> Literal["rag", "response"]:
        prompt = [
            {
                "role": "system",
                "content": "Return exactly one word: rag if legal document retrieval is needed, otherwise response.",
            },
            *messages,
        ]
        decision = (await self.complete(prompt)).strip().lower()
        return "rag" if decision == "rag" else "response"

    async def response(self, messages: list[ChatMessage]) -> str:
        base_url = settings.LLM_BASE_URL
        url = base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        headers = {"Authorization": "Bearer no-key"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT_SECONDS)) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]
