"""create feedback table

Revision ID: 0006_create_feedback
Revises: 0005_create_products
Create Date: 2025-05-27 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0006_create_feedback"
down_revision: str | None = "0005_create_products"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column(
            "id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column(
            "search_history_id",
            UUID(as_uuid=True),
            sa.ForeignKey("search_history.id"),
            nullable=True,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])
    op.create_index("ix_feedback_search_history_id", "feedback", ["search_history_id"])


def downgrade() -> None:
    op.drop_index("ix_feedback_search_history_id", table_name="feedback")
    op.drop_index("ix_feedback_user_id", table_name="feedback")
    op.drop_table("feedback")
