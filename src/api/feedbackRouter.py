from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import getDb
from src.db.models.feedback import Feedback
from src.db.models.user import User
from src.core.config import settings
from src.core.logger import logger
from src.core.dependencies import getCurrentUser

router = APIRouter(tags=["feedback"])


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    message: str | None = None


class FeedbackResponse(BaseModel):
    status: str = "ok"


class FeedbackItem(BaseModel):
    id: int
    user_id: str | None
    rating: int
    comment: str | None
    created_at: str


@router.post("/feedback", response_model=FeedbackResponse, summary="Отправить отзыв", description="Сохраняет оценку (1–5) и опциональный комментарий. Требует авторизации.")
async def submitFeedback(
    data: FeedbackRequest,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    feedback = Feedback(
        user_id=currentUser.id,
        rating=data.rating,
        comment=data.message,
    )
    db.add(feedback)
    await db.commit()
    logger.info(f"Feedback saved: rating={data.rating}, user={currentUser.email}")
    return FeedbackResponse()


@router.get("/feedback", response_model=List[FeedbackItem], summary="Список отзывов (admin)", description="Возвращает все отзывы, отсортированные от новых к старым. Доступно только администратору (`ADMIN_EMAIL`).")
async def getFeedback(
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    if not settings.ADMIN_EMAIL or currentUser.email != settings.ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    result = await db.execute(
        select(Feedback).order_by(Feedback.created_at.desc())
    )
    rows = result.scalars().all()
    logger.info(f"Feedback list requested by admin {currentUser.email}: {len(rows)} entries")

    return [
        FeedbackItem(
            id=row.id,
            user_id=str(row.user_id) if row.user_id else None,
            rating=row.rating,
            comment=row.comment,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]
