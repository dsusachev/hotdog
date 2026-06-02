import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import getCurrentUser
from src.core.security import createAccessToken, hashPasswordAsync, verifyPasswordAsync
from src.db.database import getDb
from src.db.models.user import User
from src.schemas.user import (
    TokenResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
)

logger = logging.getLogger("hotdog")
router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=UserResponse,
    summary="Регистрация нового пользователя",
    description="Создаёт аккаунт по email и паролю. Возвращает профиль без токена — после регистрации нужно войти через `/auth/login`.",
)
async def register(data: UserCreateRequest, db: AsyncSession = Depends(getDb)):
    logger.info(f"Registration attempt: {data.email}")
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        logger.warning(f"Registration failed - email already exists: {data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = await hashPasswordAsync(data.password)
    user = User(
        email=data.email,
        password_hash=hashed,
        display_name=data.display_name,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"User registered successfully: {data.email}")
    return user


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Возвращает JWT Bearer-токен. Передавайте его в заголовке `Authorization: Bearer <token>` для защищённых запросов.",
)
async def login(data: UserLoginRequest, db: AsyncSession = Depends(getDb)):
    logger.info(f"Login attempt: {data.email}")
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not await verifyPasswordAsync(data.password, user.password_hash):
        logger.warning(f"Login failed - invalid credentials: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    token = createAccessToken(data={"sub": user.email})
    logger.info(f"User logged in successfully: {data.email}")
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/auth/me",
    response_model=UserResponse,
    summary="Профиль текущего пользователя",
    description="Возвращает данные аутентифицированного пользователя по JWT-токену.",
)
async def getMe(currentUser: User = Depends(getCurrentUser)):
    return currentUser
