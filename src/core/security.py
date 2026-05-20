from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashPassword(password: str) -> str:
    """Шифрует пароль через bcrypt"""
    return pwd_context.hash(password)


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    """Проверяет пароль против хэша"""
    return pwd_context.verify(plainPassword, hashedPassword)


def createAccessToken(data: dict, expiresDelta: Optional[timedelta] = None) -> str:
    """Создаёт JWT токен"""
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.utcnow() + expiresDelta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, settings.SECRET_KEY, algorithm="HS256")


def decodeAccessToken(token: str) -> Optional[dict]:
    """Декодирует JWT токен, возвращает None если невалидный"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
