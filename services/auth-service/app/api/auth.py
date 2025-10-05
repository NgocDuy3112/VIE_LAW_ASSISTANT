from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime

from app.core.db import get_db
from app.core.security import hash_password, verify_password
from app.core.tokens import create_access_token, create_refresh_token, get_token_hash
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import RegisterRequest, LogInRequest, RefreshTokenRequest, TokenResponse


auth_router = APIRouter(prefix="/auth", tags=["auth"])



@auth_router.post("/register", status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    q = select(User).filter_by(email=payload.email)
    result = await db.execute(q)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        username=payload.username,
        email=payload.email, 
        password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}



@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LogInRequest, db: AsyncSession = Depends(get_db)):
    q = select(User).filter_by(email=payload.email)
    result = await db.execute(q)
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    revoke_query = update(RefreshToken).where(
        (RefreshToken.user_id == user.id) &
        (RefreshToken.revoked == False)
    )
    await db.execute(revoke_query)

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



@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    token_hash = get_token_hash(payload.refresh_token)

    # 1. Look up the token record by hash
    q = select(RefreshToken).filter_by(token_hash=token_hash)
    result = await db.execute(q)
    rt_record = result.scalar_one_or_none()

    # --- VALIDATION CHECKS ---
    
    # Check 1: Token existence
    if not rt_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Check 2: Token expiry
    if rt_record.expires_at < datetime.now():
        # Clean up the expired token from the DB for hygiene
        await db.execute(delete(RefreshToken).where(RefreshToken.id == rt_record.id))
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    # Check 3: Token revocation (Critical for detecting reuse/compromise)
    if rt_record.revoked:
        # Compromise detected: immediately revoke ALL tokens for this user
        revoke_all_q = update(RefreshToken).where(RefreshToken.user_id == rt_record.user_id).values(revoked=True)
        await db.execute(revoke_all_q)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token reuse detected. All sessions terminated.")

    # --- TOKEN ROTATION & ISSUANCE ---

    # A. Revoke the token that was just used (single-use token)
    rt_record.revoked = True

    # B. Generate a new pair of tokens
    user_id_str = str(rt_record.user_id)
    new_access = create_access_token(user_id_str)
    new_refresh_data = create_refresh_token()

    # C. Create and save the new Refresh Token record
    new_rt_record = RefreshToken(
        user_id=rt_record.user_id,
        token_hash=new_refresh_data["token_hash"],
        issued_at=new_refresh_data["issued_at"],
        expires_at=new_refresh_data["expires_at"],
    )
    db.add(new_rt_record)

    # D. Commit changes and return new tokens
    await db.commit()
    return {"access_token": new_access, "refresh_token": new_refresh_data["token"]}



@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Revokes the provided Refresh Token, ending the user's persistent session.
    """
    refresh_token_raw = payload.refresh_token
    token_hash = get_token_hash(refresh_token_raw)

    # Find the token by hash and mark it as revoked (only if it's not already revoked)
    q = update(RefreshToken).where(
        (RefreshToken.token_hash == token_hash) &
        (RefreshToken.revoked == False)
    ).values(revoked=True)
    
    await db.execute(q)
    await db.commit()
    
    # Return 204 No Content. We don't signal success/failure based on whether a token was found 
    # for security reasons (to avoid leaking information).
    return