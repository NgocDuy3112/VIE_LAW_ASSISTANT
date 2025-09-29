from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.core.db import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(length=128), nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="refresh_tokens", lazy="joined")