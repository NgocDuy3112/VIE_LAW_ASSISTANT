from typing import Literal
import aiohttp

from config import settings

ChatMessage = dict[str, str]


class ChatModel:
    def __init__(self, model_name: str, temperature: float = 0.1):
        self.provider, self.model = model_name.split("/", 1)
        self.temperature = temperature

    async def complete(self, messages: list[ChatMessage]) -> str:
        if self.provider == "ollama":
            return await self._complete_openai_compatible(
                base_url=settings.OLLAMA_BASE_URL or "http://localhost:11434/v1",
                messages=messages,
            )
        if self.provider in {"lmstudio", "lm-studio", "lm_studio"}:
            return await self._complete_openai_compatible(
                base_url=settings.LM_STUDIO_BASE_URL or "http://localhost:1234/v1",
                messages=messages,
            )
        raise ValueError(f"Unsupported model provider without LangChain: {self.provider}")

    async def route(self, messages: list[ChatMessage]) -> Literal["rag", "response"]:
        prompt = [
            {
                "role": "system",
                "content": "Return exactly one word: rag if legal document retrieval is needed, otherwise response.",
            },
            *messages,
        ]
        decision = (await self.complete(prompt)).strip().lower()
        return "rag" if "rag" in decision else "response"

    async def _complete_openai_compatible(self, base_url: str | None, messages: list[ChatMessage]) -> str:
        url = (base_url or "http://localhost:1234/v1").rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=settings.REQUEST_TIMEOUT_SECONDS) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]
