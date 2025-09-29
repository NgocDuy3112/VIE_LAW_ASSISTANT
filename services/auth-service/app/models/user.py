from sqlalchemy import Column, String, Boolean, DateTime, UUID, func
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.core.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    username = Column(String(length=320), unique=True, index=True, nullable=False)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    password_hash = Column(String(length=256), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )