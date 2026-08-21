"""API schemas for catalog sync jobs."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import SyncJobLogLevel, SyncJobStatus


class SyncJobLogEntry(BaseModel):
    """A single progress or error line from a sync job."""

    at: datetime
    level: SyncJobLogLevel
    message: str


class SyncJobRead(BaseModel):
    """Public view of a persisted sync job."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: str
    status: SyncJobStatus
    fetched: int | None = None
    inserted: int | None = None
    skipped: int | None = None
    error: str | None = None
    logs: list[SyncJobLogEntry] = Field(default_factory=list)
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class StartSyncResponse(BaseModel):
    """Returned immediately after a sync job is queued."""

    job_id: uuid.UUID = Field(description="Identifier used to poll job status")
