from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class FeedbackCreateRequest(BaseModel):
    search_history_id: Optional[UUID] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[UUID] = None
    search_history_id: Optional[UUID] = None
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
