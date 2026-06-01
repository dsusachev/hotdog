from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import getDb
from src.db.models.user import User
from src.core.security import decodeAccessToken

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2SchemeOptional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def getCurrentUser(
    token: str = Depends(oauth2Scheme),
    db: AsyncSession = Depends(getDb),
) -> User:
    payload = decodeAccessToken(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Невалидный токен")

    result = await db.execute(select(User).where(User.email == sub))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт заблокирован")

    return user


async def getCurrentUserOptional(
    token: str | None = Depends(oauth2SchemeOptional),
    db: AsyncSession = Depends(getDb),
) -> User | None:
    if not token:
        return None
    payload = decodeAccessToken(token)
    if not payload:
        return None
    userId = payload.get("sub")
    if not userId:
        return None
    result = await db.execute(select(User).where(User.email == userId))
    return result.scalar_one_or_none()
