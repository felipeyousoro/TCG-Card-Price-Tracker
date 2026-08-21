"""Catalog listing for registered importers."""

from pydantic import BaseModel, ConfigDict

from .jobs.schemas import SyncJobRead


class ImporterInfo(BaseModel):
    """A registered catalog source the admin shell can sync."""

    model_config = ConfigDict(extra="forbid")

    source: str
    label: str
    description: str
    latest_job: SyncJobRead | None = None
