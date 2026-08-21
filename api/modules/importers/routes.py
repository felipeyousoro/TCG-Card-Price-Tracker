"""HTTP routes for listing importers and running background sync jobs."""

import asyncio
import uuid

from fastapi import APIRouter, status
from sqlalchemy.exc import IntegrityError

from ...common.exceptions import ValidationError
from ...common.utils.error_handler import handle_exception
from ...core.auth.http_exceptions import HTTPException, NotFoundException
from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .jobs.runner import run_sync_job
from .jobs.schemas import StartSyncResponse, SyncJobRead
from .jobs.service import create_job, get_active_job_for_source, get_job, get_latest_job
from .registry import get_importer, list_importer_catalog
from .schemas import ImporterInfo

router = APIRouter(prefix="/importers", tags=["Importers"])


@router.get(
    "/",
    response_model=list[ImporterInfo],
    summary="List catalog importers",
    description="Returns registered importer sources and the latest sync job for each.",
)
async def list_importers(
    db: AsyncSessionDep,
    _: CurrentUserDep,
) -> list[ImporterInfo]:
    """List importer sources with their most recent job."""
    items: list[ImporterInfo] = []
    for entry in list_importer_catalog():
        latest = await get_latest_job(db, entry["source"])
        items.append(
            ImporterInfo(
                source=entry["source"],
                label=entry["label"],
                description=entry["description"],
                latest_job=SyncJobRead.model_validate(latest) if latest else None,
            )
        )
    return items


@router.post(
    "/{source}/sync",
    response_model=StartSyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue a catalog sync",
    description="Creates a sync job and runs the importer in the background.",
    responses={
        202: {"description": "Sync job queued"},
        401: {"description": "Not authenticated"},
        409: {"description": "A sync is already in progress for this source"},
        422: {"description": "Unknown importer source"},
    },
)
async def start_sync(
    source: str,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
) -> StartSyncResponse:
    """Queue a background catalog sync for the given source."""
    try:
        get_importer(source)
    except ValidationError as exc:
        http_exception = handle_exception(exc)
        if http_exception:
            raise http_exception
        raise

    normalized = source.strip().lower()
    active = await get_active_job_for_source(db, normalized)
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A sync is already in progress for this source.",
        )

    try:
        job = await create_job(db, source=normalized, user_id=current_user["id"])
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A sync is already in progress for this source.",
        ) from None

    asyncio.create_task(run_sync_job(job.id))
    return StartSyncResponse(job_id=job.id)


@router.get(
    "/jobs/{job_id}",
    response_model=SyncJobRead,
    summary="Get sync job status",
    description="Poll this endpoint until the job is succeeded or failed.",
    responses={
        200: {"description": "Current job status"},
        401: {"description": "Not authenticated"},
        404: {"description": "Job not found"},
    },
)
async def get_sync_job(
    job_id: uuid.UUID,
    db: AsyncSessionDep,
    _: CurrentUserDep,
) -> SyncJobRead:
    """Return the current state of a sync job."""
    job = await get_job(db, job_id)
    if job is None:
        raise NotFoundException(detail="Sync job not found")
    return SyncJobRead.model_validate(job)
