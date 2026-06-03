import asyncio
from datetime import datetime, timedelta, timezone
from functools import partial

import bcrypt
from jose import JWTError, jwt

from src.core.config import settings


def hashPassword(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return bcrypt.checkpw(plainPassword.encode("utf-8"), hashedPassword.encode("utf-8"))


def createAccessToken(data: dict, expiresDelta: timedelta | None = None) -> str:
    """Создаёт JWT токен"""
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.now(timezone.utc) + expiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, settings.SECRET_KEY, algorithm="HS256")


def decodeAccessToken(token: str) -> dict | None:
    """Декодирует JWT токен, возвращает None если невалидный"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


# ========== АСИНХРОННЫЕ ОБЁРТКИ ДЛЯ ИСПОЛЬЗОВАНИЯ В FASTAPI ==========


async def hashPasswordAsync(password: str) -> str:
    """Асинхронная обёртка для hashPassword"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, hashPassword, password)


async def verifyPasswordAsync(plainPassword: str, hashedPassword: str) -> bool:
    """Асинхронная обёртка для verifyPassword"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, partial(verifyPassword, plainPassword, hashedPassword)
    )
