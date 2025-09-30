import hashlib
import pytest
from sqlalchemy import select
from app.config import settings


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import ORM metadata and models after env is configured
from app.core.db import Base, engine as app_engine
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.tokens import create_refresh_token



@pytest.mark.asyncio
async def test_refresh_token_persistence_and_hash_match():
    """
    Create an in-memory DB, create tables, insert a user and a refresh token
    and verify that the token_hash stored in DB matches sha256(raw_token).
    """

    # Use the same URL as we set above (in-memory). Note: app_engine was created on import with the env var.
    test_engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)

    # Create tables in the in-memory DB
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Use a local session factory backed by the test engine
    TestSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async with TestSessionLocal() as session:
        # Create a user (minimal required fields — adapt if your User requires other args)
        user = User(email="test@example.com", username="testuser", password_hash="hashed")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create a refresh token using app logic
        refresh = create_refresh_token()
        raw_token = refresh["token"]
        expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        rt = RefreshToken(
            user_id=user.id,
            token_hash=refresh["token_hash"],
            issued_at=refresh["issued_at"],
            expires_at=refresh["expires_at"],
        )
        session.add(rt)
        await session.commit()

        # Query back the stored refresh token and assert the stored hash equals expected_hash
        q = select(RefreshToken).filter_by(user_id=user.id)
        result = await session.execute(q)
        stored_rt = result.scalar_one_or_none()

        assert stored_rt is not None, "RefreshToken was not persisted"
        assert stored_rt.token_hash == expected_hash, "Stored token_hash doesn't match sha256(raw_token)"

    # Dispose the test engine
    await test_engine.dispose()