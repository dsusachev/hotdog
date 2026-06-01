from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import getDb
from src.db.models.feedback import Feedback
from src.db.models.user import User
from src.core.logger import logger
from src.core.dependencies import getCurrentUser

router = APIRouter()


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    message: str | None = None


class FeedbackResponse(BaseModel):
    status: str = "ok"


@router.post("/feedback", response_model=FeedbackResponse)
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
