from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

from app.schemas.chat_history import ChatHistoryRequest, ChatHistoryResponse
from app.config import *


class ChatHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create(self, request: ChatHistoryRequest):
        query = text("""
            INSERT INTO chat_history (id, user_id, session_id, question, answer, timestamp)
            VALUES (gen_random_uuid(), :user_id, :session_id, :question, :answer, :timestamp)
            RETURNING id, user_id, session_id, question, answer, timestamp
        """)
        result = await self.db.execute(query, request.model_dump())
        await self.db.commit()
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Player insert failed")
        await self.db.commit()


    async def get_chat_history(self, user_id: UUID | None = None, session_id: UUID | None = None) -> list[ChatHistoryResponse]:
        conditions = []
        params = {}
        if user_id:
            conditions.append("user_id = :user_id")
            params["user_id"] = user_id
        if session_id:
            conditions.append("session_id = :session_id")
            params["session_id"] = session_id
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = text(f"""
            SELECT id, user_id, session_id, question, answer, timestamp
            FROM chat_history
            WHERE {where_clause}
            ORDER BY timestamp DESC
        """)
        result = await self.db.execute(query, params)
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Chat history not found")
        return [ChatHistoryResponse(**dict(row)) for row in rows]


    async def delete_chat_history(self, user_id: UUID | None = None, session_id: UUID | None = None) -> int:
        if not user_id and not session_id:
            raise ValueError("At least one of 'user_id' or 'session_id' must be provided for deletion.")
        conditions = []
        params = {}
        if user_id:
            conditions.append("user_id = :user_id")
            params["user_id"] = user_id
        if session_id:
            conditions.append("session_id = :session_id")
            params["session_id"] = session_id
        where_clause = " AND ".join(conditions)
        query = text(f"""
            DELETE FROM chat_history
            WHERE {where_clause}
        """)
        result = await self.db.execute(query, params)
        await self.db.commit()
        if not result.rowcount or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Chat history not found for deletion")
        return result.rowcount