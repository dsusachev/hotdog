import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.db.database import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_points = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SprintItem(Base):
    __tablename__ = "sprint_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sprint_id = Column(
        UUID(as_uuid=True), ForeignKey("sprints.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(300), nullable=False)
    points = Column(Integer, nullable=False, default=1)
    is_done = Column(Boolean, nullable=False, default=False)
    done_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
