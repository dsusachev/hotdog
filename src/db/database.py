import ssl

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import settings

# On Linux, asyncpg's default SSL negotiation can hang and time out when
# connecting to cloud PostgreSQL (Supabase). An explicit SSLContext skips
# the negotiation and goes straight to the TLS handshake.
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"ssl": _ssl_context, "statement_cache_size": 0},
)

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
