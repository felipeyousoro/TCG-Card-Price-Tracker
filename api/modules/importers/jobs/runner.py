"""In-process runner for catalog sync jobs."""

import logging
import uuid

from ....core.database.session import local_session
from ..registry import get_importer
from . import service as job_service

logger = logging.getLogger(__name__)


async def run_sync_job(job_id: uuid.UUID) -> None:
    """Execute a queued sync job using a dedicated database session."""
    source: str | None = None
    try:
        async with local_session() as db:
            job = await job_service.mark_running(db, job_id)
            if job is None:
                logger.error("Sync job %s was not found", job_id)
                return
            source = job.source

        importer = get_importer(source)
        async with local_session() as db:
            result = await importer.import_all_sets(db)

        async with local_session() as db:
            await job_service.mark_succeeded(db, job_id, result)
    except Exception:
        logger.exception("Sync job %s failed", job_id)
        async with local_session() as db:
            await job_service.mark_failed(db, job_id, "Catalog sync failed. Check server logs for details.")
