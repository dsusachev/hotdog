from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

asyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def getDb():
    async with asyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
