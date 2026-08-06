from collections.abc import AsyncGenerator


async def stream_text(text: str) -> AsyncGenerator[str, None]:
    yield text
