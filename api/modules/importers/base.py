from typing import Protocol

from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession


class ImportResult(BaseModel):
    """Outcome of an OPTCG catalog import run."""

    model_config = ConfigDict(extra="forbid")

    source: str
    fetched: int
    inserted: int
    skipped: int


class OptcgImporter(Protocol):
    """Source adapter that loads cards into the shared OPTCG catalog."""

    source: str

    async def import_all_sets(self, db: AsyncSession) -> ImportResult:
        """Fetch cards from the source and insert missing catalog rows."""
        ...
