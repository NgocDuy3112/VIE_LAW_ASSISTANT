import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[Literal[uuid.UUID]] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Literal[uuid.UUID]] = mapped_column(UUID(as_uuid=True), index=True)
    title: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[Literal[uuid.UUID]] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[Literal[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["ChatSession"] = relationship(back_populates="messages")


from typing import Literal
