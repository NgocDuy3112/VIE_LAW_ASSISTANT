from collections.abc import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession



async def get_postgresql_async_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async_session = request.app.state.postgresql_async_session
    async with async_session() as session:
        yield session