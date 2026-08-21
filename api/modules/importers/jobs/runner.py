"""In-process runner for catalog sync jobs."""

import asyncio
import logging
import uuid

from ....core.database.session import local_session
from ..registry import get_importer
from . import service as job_service
from .enums import SyncJobLogLevel

logger = logging.getLogger(__name__)


async def run_sync_job(job_id: uuid.UUID) -> None:
    """Execute a queued sync job using a dedicated database session."""
    source: str | None = None

    async def on_progress(message: str) -> None:
        async with local_session() as db:
            await job_service.append_log(db, job_id, message, SyncJobLogLevel.INFO)

    try:
        await asyncio.sleep(0)
        async with local_session() as db:
            job = await job_service.mark_running(db, job_id)
            if job is None:
                logger.error("Sync job %s was not found", job_id)
                return
            source = job.source

        importer = get_importer(source)
        async with local_session() as db:
            result = await importer.import_all_sets(db, on_progress=on_progress)

        async with local_session() as db:
            await job_service.mark_succeeded(db, job_id, result)
    except Exception as exc:
        logger.exception("Sync job %s failed", job_id)
        reason = str(exc).strip() or type(exc).__name__
        async with local_session() as db:
            await job_service.mark_failed(db, job_id, f"Catalog sync failed: {reason}")
