from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import getDb
from src.db.models.search_history import SearchHistory
from src.db.models.user import User
from src.core.logger import logger
from src.core.dependencies import getCurrentUser

router = APIRouter()


class HistoryEntry(BaseModel):
    id: str
    label: str
    query: str
    confidence: float | None
    created_at: str


@router.get("/history", response_model=List[HistoryEntry])
async def getHistory(
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    result = await db.execute(
        select(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(50)
    )
    rows = result.scalars().all()
    logger.info(f"History requested: {len(rows)} entries")

    entries = []
    for row in rows:
        ml = row.raw_ml_response or {}
        entries.append(HistoryEntry(
            id=str(row.id),
            label=ml.get("category") or "Неизвестно",
            query=row.query_text or "",
            confidence=ml.get("confidence"),
            created_at=row.created_at.isoformat(),
        ))
    return entries
