from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from app.schemas.chat_history import ChatHistoryRequest, ChatHistoryResponse
from app.helpers.embedding import embed_query  # your embedding function
from app.config import *



class ChatHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_history(self, request: ChatHistoryRequest):
        # Embed the question
        embedding = embed_query(request.question)
        query = text("""
            INSERT INTO chat_history (id, user_id, session_id, question, question_embedding, answer, timestamp)
            VALUES (gen_random_uuid(), :user_id, :session_id, :question, :embedding, :answer, :timestamp)
            RETURNING id, user_id, session_id, question, answer, timestamp
        """)
        params = {
            **request.model_dump(),
            "embedding": embedding.tolist()
        }
        result = await self.db.execute(query, params)
        await self.db.commit()
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=500, detail="Insert failed")
        return ChatHistoryResponse(**dict(row))

    async def get_chat_history(
        self,
        user_id: UUID | None = None,
        session_id: UUID | None = None,
        limit: int | None = None
    ) -> list[ChatHistoryResponse]:
        conditions = []
        params = {"limit": limit}
        params["limit"] = limit if limit else 3
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
            LIMIT :limit
        """)

        result = await self.db.execute(query, params)
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Chat history not found")
        return [ChatHistoryResponse(**dict(row)) for row in rows]

    async def delete_chat_history(
        self,
        user_id: UUID | None = None,
        session_id: UUID | None = None
    ) -> int:
        if not user_id and not session_id:
            raise HTTPException(status_code=400, detail="Must provide user_id or session_id")
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
        if not result.rowcount:
            raise HTTPException(status_code=404, detail="No rows deleted")
        return result.rowcount

    async def search_similar_questions(self, user_id: UUID, query: str, top_k: int = 5) -> list[ChatHistoryResponse]:
        query_embedding = embed_query(query).tolist()
        result = await self.db.execute(text("""
            SELECT id, user_id, session_id, question, answer, timestamp
            FROM chat_history
            WHERE user_id = :user_id
            ORDER BY question_embedding <#> :embedding
            LIMIT :top_k
        """), {
            "user_id": user_id,
            "embedding": query_embedding,
            "top_k": top_k
        })
        rows = result.fetchall()
        return [ChatHistoryResponse(**dict(row)) for row in rows]