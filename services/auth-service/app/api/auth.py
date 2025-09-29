from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.core.security import hash_password, verify_password
from app.core.tokens import create_access_token, create_refresh_token
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import RegisterIn, TokenOut



router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    q = select(User).filter_by(email=payload.email)
    result = await db.execute(q)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenOut)
async def login(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    q = select(User).filter_by(email=payload.email)
    result = await db.execute(q)
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token()

    rt = RefreshToken(
        user_id=user.id,
        token_hash=refresh["token_hash"],
        issued_at=refresh["issued_at"],
        expires_at=refresh["expires_at"],
    )
    db.add(rt)
    await db.commit()
    return {"access_token": access, "refresh_token": refresh["token"]}