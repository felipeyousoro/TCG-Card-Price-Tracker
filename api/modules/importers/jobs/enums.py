"""Persisted in-process catalog sync jobs."""

from enum import StrEnum


class SyncJobStatus(StrEnum):
    """Lifecycle of a catalog sync job."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


ACTIVE_SYNC_STATUSES: tuple[str, ...] = (SyncJobStatus.QUEUED.value, SyncJobStatus.RUNNING.value)
TERMINAL_SYNC_STATUSES: tuple[str, ...] = (SyncJobStatus.SUCCEEDED.value, SyncJobStatus.FAILED.value)
