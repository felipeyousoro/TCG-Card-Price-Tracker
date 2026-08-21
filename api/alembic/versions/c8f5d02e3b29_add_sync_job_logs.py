"""add sync job logs

Revision ID: c8f5d02e3b29
Revises: b7e4c91a2d18
Create Date: 2026-08-21 18:17:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c8f5d02e3b29"
down_revision: Union[str, None] = "b7e4c91a2d18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sync_job",
        sa.Column(
            "logs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("sync_job", "logs")
