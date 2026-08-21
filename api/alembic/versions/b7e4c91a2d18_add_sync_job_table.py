"""add sync_job table

Revision ID: b7e4c91a2d18
Revises: a4f8c2e91b07
Create Date: 2026-08-21 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b7e4c91a2d18"
down_revision: Union[str, None] = "a4f8c2e91b07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_job",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("fetched", sa.Integer(), nullable=True),
        sa.Column("inserted", sa.Integer(), nullable=True),
        sa.Column("skipped", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_job_source"), "sync_job", ["source"], unique=False)
    op.create_index(op.f("ix_sync_job_created_by_user_id"), "sync_job", ["created_by_user_id"], unique=False)
    op.create_index(
        "uq_sync_job_active_source",
        "sync_job",
        ["source"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued', 'running')"),
    )


def downgrade() -> None:
    op.drop_index("uq_sync_job_active_source", table_name="sync_job")
    op.drop_index(op.f("ix_sync_job_created_by_user_id"), table_name="sync_job")
    op.drop_index(op.f("ix_sync_job_source"), table_name="sync_job")
    op.drop_table("sync_job")
