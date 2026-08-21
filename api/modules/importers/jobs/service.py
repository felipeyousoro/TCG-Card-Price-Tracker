"""Persistence helpers for catalog sync jobs."""

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database.session import local_session
from ....modules.importers.base import ImportResult
from .enums import ACTIVE_SYNC_STATUSES, SyncJobStatus
from .models import SyncJob

logger = logging.getLogger(__name__)

CRASH_MESSAGE = "Job interrupted because the API process restarted."


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


async def create_job(db: AsyncSession, source: str, user_id: int) -> SyncJob:
    """Insert a queued sync job and return it."""
    job = SyncJob(source=source, created_by_user_id=user_id, status=SyncJobStatus.QUEUED.value)
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
    await db.commit()


async def mark_failed(db: AsyncSession, job_id: uuid.UUID, error: str) -> None:
    """Store a failure reason on the job."""
    job = await get_job(db, job_id)
    if job is None:
        return
    job.status = SyncJobStatus.FAILED.value
    job.error = error[:2000]
    job.finished_at = datetime.now(UTC)
    await db.commit()


async def fail_stale_sync_jobs() -> None:
    """Fail jobs that were still active when the process last died."""
    now = datetime.now(UTC)
    async with local_session() as db:
        result = await db.execute(
            update(SyncJob)
            .where(SyncJob.status.in_(ACTIVE_SYNC_STATUSES))
            .values(status=SyncJobStatus.FAILED.value, error=CRASH_MESSAGE, finished_at=now)
        )
        await db.commit()
        if result.rowcount:
            logger.warning("Marked %s stale sync job(s) as failed", result.rowcount)
