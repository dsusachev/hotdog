from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.db.database import getDb
from src.db.models.user import User
from src.core.security import hashPassword, verifyPassword, createAccessToken
from src.core.dependencies import getCurrentUser
from src.api.schemas import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    TokenResponse,
    UserMeResponse,
)
from src.core.logger import logger

router = APIRouter()


@router.post("/auth/register", response_model=UserRegisterResponse)
async def register(data: UserRegisterRequest, db: AsyncSession = Depends(getDb)):
    logger.info(f"Registration attempt: {data.email}")

    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    user = User(
        id=uuid.uuid4(),
        email=data.email,
        password_hash=hashPassword(data.password),
        display_name=data.display_name,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User registered: {user.email}")
    return UserRegisterResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(getDb)):
    logger.info(f"Login attempt: {data.email}")

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verifyPassword(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    token = createAccessToken({"sub": str(user.id), "email": user.email})

    logger.info(f"User logged in: {user.email}")
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserMeResponse)
async def getMe(currentUser: User = Depends(getCurrentUser)):
    return UserMeResponse(
        id=str(currentUser.id),
        email=currentUser.email,
        display_name=currentUser.display_name,
        is_active=currentUser.is_active,
    )
