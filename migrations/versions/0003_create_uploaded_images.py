"""create uploaded_images table

Revision ID: 0003_create_uploaded_images
Revises: 0002_create_search_history
Create Date: 2025-05-13 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision: str = "0003_create_uploaded_images"
down_revision: Union[str, None] = "0002_create_search_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "uploaded_images",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("storage_path", sa.String(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_uploaded_images_user_id", "uploaded_images", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_uploaded_images_user_id", table_name="uploaded_images")
    op.drop_table("uploaded_images")
