"""Persistence helpers for catalog sync jobs."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database.session import local_session
from ....modules.importers.base import ImportResult
from .enums import ACTIVE_SYNC_STATUSES, SyncJobLogLevel, SyncJobStatus
from .models import SyncJob

logger = logging.getLogger(__name__)

CRASH_MESSAGE = "Job interrupted because the API process restarted."
MAX_LOG_LINES = 200
MAX_ERROR_LENGTH = 2000


def _log_entry(level: SyncJobLogLevel | str, message: str) -> dict[str, Any]:
    return {
        "at": datetime.now(UTC).isoformat(),
        "level": SyncJobLogLevel(level).value,
        "message": message[:MAX_ERROR_LENGTH],
    }


def _append_to_job(job: SyncJob, level: SyncJobLogLevel | str, message: str) -> None:
    current = list(job.logs or [])
    current.append(_log_entry(level, message))
    if len(current) > MAX_LOG_LINES:
        current = current[-MAX_LOG_LINES:]
    job.logs = current


async def get_job(db: AsyncSession, job_id: uuid.UUID) -> SyncJob | None:
    """Load a sync job by id."""
    return await db.get(SyncJob, job_id)


async def get_latest_job(db: AsyncSession, source: str) -> SyncJob | None:
    """Return the most recently created job for a source, if any."""
    result = await db.execute(
        select(SyncJob).where(SyncJob.source == source).order_by(SyncJob.created_at.desc()).limit(1)
    )
    return result.scalar_one_or_none()


async def get_active_job_for_source(db: AsyncSession, source: str) -> SyncJob | None:
    """Return a queued or running job for the source, if one exists."""
    result = await db.execute(
        select(SyncJob)
        .where(SyncJob.source == source, SyncJob.status.in_(ACTIVE_SYNC_STATUSES))
        .order_by(SyncJob.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def append_log(
    db: AsyncSession,
    job_id: uuid.UUID,
    message: str,
    level: SyncJobLogLevel | str = SyncJobLogLevel.INFO,
) -> None:
    """Append a log line to a job and commit immediately so the UI can poll it."""
    job = await get_job(db, job_id)
    if job is None:
        return
    _append_to_job(job, level, message)
    await db.commit()


async def create_job(db: AsyncSession, source: str, user_id: int) -> SyncJob:
    """Insert a queued sync job and return it."""
    job = SyncJob(source=source, created_by_user_id=user_id, status=SyncJobStatus.QUEUED.value)
    _append_to_job(job, SyncJobLogLevel.INFO, "Queued catalog sync")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def mark_running(db: AsyncSession, job_id: uuid.UUID) -> SyncJob | None:
    """Mark a queued job as running."""
    job = await get_job(db, job_id)
    if job is None:
        return None
    job.status = SyncJobStatus.RUNNING.value
    job.started_at = datetime.now(UTC)
    _append_to_job(job, SyncJobLogLevel.INFO, "Job started")
    await db.commit()
    await db.refresh(job)
    return job


async def mark_succeeded(db: AsyncSession, job_id: uuid.UUID, result: ImportResult) -> None:
    """Store successful import counts on the job."""
    job = await get_job(db, job_id)
    if job is None:
        return
    job.status = SyncJobStatus.SUCCEEDED.value
    job.fetched = result.fetched
    job.inserted = result.inserted
    job.skipped = result.skipped
    job.error = None
    job.finished_at = datetime.now(UTC)
    _append_to_job(
        job,
        SyncJobLogLevel.INFO,
        f"Sync finished: fetched={result.fetched} inserted={result.inserted} skipped={result.skipped}",
    )
    await db.commit()


async def mark_failed(db: AsyncSession, job_id: uuid.UUID, error: str) -> None:
    """Store a failure reason on the job."""
    job = await get_job(db, job_id)
    if job is None:
        return
    truncated = error[:MAX_ERROR_LENGTH]
    job.status = SyncJobStatus.FAILED.value
    job.error = truncated
    job.finished_at = datetime.now(UTC)
    _append_to_job(job, SyncJobLogLevel.ERROR, truncated)
    await db.commit()


async def fail_stale_sync_jobs() -> None:
    """Fail jobs that were still active when the process last died."""
    now = datetime.now(UTC)
    async with local_session() as db:
        result = await db.execute(select(SyncJob).where(SyncJob.status.in_(ACTIVE_SYNC_STATUSES)))
        jobs = result.scalars().all()
        for job in jobs:
            job.status = SyncJobStatus.FAILED.value
            job.error = CRASH_MESSAGE
            job.finished_at = now
            _append_to_job(job, SyncJobLogLevel.ERROR, CRASH_MESSAGE)
        await db.commit()
        if jobs:
            logger.warning("Marked %s stale sync job(s) as failed", len(jobs))
