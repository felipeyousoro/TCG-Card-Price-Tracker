"""Catalog listing for registered importers."""

from pydantic import BaseModel, ConfigDict

from .jobs.schemas import SyncJobRead
from .tcgplayer.groups import TcgplayerGroup


class ImporterInfo(BaseModel):
    """A registered catalog source the admin shell can sync."""

    model_config = ConfigDict(extra="forbid")

    source: str
    label: str
    description: str
    latest_job: SyncJobRead | None = None


class TcgplayerGroupRead(BaseModel):
    """One curated TCGPlayer catalog group from the OPTCG fixture."""

    model_config = ConfigDict(extra="forbid")

    name: str
    category_id: int
    group_id: int
    enabled: bool

    @classmethod
    def from_group(cls, group: TcgplayerGroup) -> "TcgplayerGroupRead":
        return cls(
            name=group.name,
            category_id=group.category_id,
            group_id=group.group_id,
            enabled=group.enabled,
        )
