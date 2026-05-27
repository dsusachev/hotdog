from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import getDb
from src.db.models.feedback import Feedback
from src.db.models.user import User
from src.core.dependencies import getCurrentUser
from src.schemas.feedback import FeedbackCreateRequest, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def createFeedback(
    data: FeedbackCreateRequest,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    feedback = Feedback(
        user_id=currentUser.id,
        search_history_id=data.search_history_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


@router.get("/feedback/my", response_model=list[FeedbackResponse])
async def getMyFeedback(
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    result = await db.execute(
        select(Feedback).where(Feedback.user_id == currentUser.id)
    )
    return result.scalars().all()
