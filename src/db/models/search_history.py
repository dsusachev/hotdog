import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from src.db.database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    image_id = Column(UUID(as_uuid=True), nullable=True)
    query_text = Column(String, nullable=True)
    recognized_product_id = Column(UUID(as_uuid=True), nullable=True)
    raw_ml_response = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
