"""ORM model for catalog sync jobs."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from ....core.database.models import TimestampMixin
from ....core.database.session import Base
from .enums import SyncJobStatus


class SyncJob(Base, TimestampMixin):
    """A catalog import run triggered from the admin shell."""

    __tablename__ = "sync_job"
    __table_args__ = (
        Index(
            "uq_sync_job_active_source",
            "source",
            unique=True,
            postgresql_where=text("status IN ('queued', 'running')"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        init=False,
    )
    source: Mapped[str] = mapped_column(String(50), index=True)
    created_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default=SyncJobStatus.QUEUED.value)
    fetched: Mapped[int | None] = mapped_column(Integer, default=None)
    inserted: Mapped[int | None] = mapped_column(Integer, default=None)
    skipped: Mapped[int | None] = mapped_column(Integer, default=None)
    error: Mapped[str | None] = mapped_column(Text, default=None)
    logs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        default_factory=list,
        server_default=text("'[]'::jsonb"),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
