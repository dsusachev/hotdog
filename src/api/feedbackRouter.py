from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import getDb
from src.db.models.feedback import Feedback
from src.core.logger import logger

router = APIRouter()


class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    message: str | None = None


class FeedbackResponse(BaseModel):
    status: str = "ok"


@router.post("/feedback", response_model=FeedbackResponse)
async def submitFeedback(data: FeedbackRequest, db: AsyncSession = Depends(getDb)):
    feedback = Feedback(rating=data.rating, message=data.message)
    db.add(feedback)
    await db.commit()
    logger.info(f"Feedback saved: rating={data.rating}")
    return FeedbackResponse()
