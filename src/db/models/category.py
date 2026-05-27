from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, nullable=False, unique=True)
