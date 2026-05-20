import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.config import settings
from src.core.logger import logger
from src.db.database import getDb

router = APIRouter()

startTime = time.time()   # <-- если нужен uptime, добавьте

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.get("/health")
async def healthCheck(db: AsyncSession = Depends(getDb)):
    uptimeSeconds = round(time.time() - startTime)
    dbStatus = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"Health check: database unavailable — {e}")
        dbStatus = "unavailable"
    overallStatus = "ok" if dbStatus == "ok" else "degraded"
    return {
        "status": overallStatus,
        "version": settings.VERSION,
        "uptime_seconds": uptimeSeconds,
        "services": {"database": dbStatus},
    }
