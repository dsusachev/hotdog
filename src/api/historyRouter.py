import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

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
    entry_type: str
    confidence: float | None
    created_at: str


@router.get("/history", response_model=List[HistoryEntry])
async def getHistory(
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == currentUser.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(50)
    )
    rows = result.scalars().all()
    logger.info(f"History requested by {currentUser.email}: {len(rows)} entries")

    entries = []
    for row in rows:
        ml = row.raw_ml_response or {}
        entries.append(HistoryEntry(
            id=str(row.id),
            label=ml.get("category") or ml.get("query") or "Неизвестно",
            query=row.query_text or "",
            entry_type=ml.get("type", "classify"),
            confidence=ml.get("confidence"),
            created_at=row.created_at.isoformat(),
        ))
    return entries


@router.delete("/history/{historyId}", status_code=204)
async def deleteHistoryEntry(
    historyId: str,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    try:
        entry_uuid = uuid.UUID(historyId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат id")

    result = await db.execute(
        select(SearchHistory).where(
            SearchHistory.id == entry_uuid,
            SearchHistory.user_id == currentUser.id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    await db.delete(entry)
    await db.commit()
    logger.info(f"History entry {historyId} deleted by {currentUser.email}")
