"""create search_history table

Revision ID: 0002_create_search_history
Revises: 0001_create_users
Create Date: 2025-05-13 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from alembic import op

revision: str = "0002_create_search_history"
down_revision: Union[str, None] = "0001_create_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "search_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("image_id", UUID(as_uuid=True), nullable=True),
        sa.Column("query_text", sa.String(), nullable=True),
        sa.Column("recognized_product_id", UUID(as_uuid=True), nullable=True),
        sa.Column("raw_ml_response", JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_search_history_user_id", table_name="search_history")
    op.drop_table("search_history")
