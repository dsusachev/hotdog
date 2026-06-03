from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    search_history_id: UUID | None = None
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    user_id: UUID | None = None
    search_history_id: UUID | None = None
    rating: int
    comment: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
