import asyncio

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ....common.exceptions import ValidationError
from ....modules.optcg.schemas import OptcgCardCreate
from ....modules.optcg.service import OptcgCatalogService
from ..base import ImportResult, ProgressCallback
from .client import OptcgApiClient
from .mapper import to_card_create


class OptcgApiImporter:
    """Loads OPTCG catalog cards from optcgapi.com into the shared domain."""

    source = "optcgapi"

    def __init__(self, client: OptcgApiClient, catalog: OptcgCatalogService) -> None:
        self._client = client
        self._catalog = catalog

    async def import_all_sets(
        self,
        db: AsyncSession,
        *,
        on_progress: ProgressCallback | None = None,
    ) -> ImportResult:
        """Fetch all set cards, map them, and insert missing catalog rows."""
        await _emit(on_progress, "Fetching all set cards from optcgapi.com")
        raw_cards = await self._client.fetch_all_set_cards()
        await _emit(on_progress, f"Fetched {len(raw_cards)} cards")
        await _emit(on_progress, "Mapping card payloads")
        cards, invalid = await asyncio.to_thread(_map_cards, raw_cards)
        if invalid:
            await _emit(on_progress, f"Skipped {invalid} invalid card payloads")

        await _emit(on_progress, "Inserting missing catalog rows")
        inserted, skipped = await self._catalog.bulk_insert_missing(cards, db)
        return ImportResult(
            source=self.source,
            fetched=len(raw_cards),
            inserted=inserted,
            skipped=skipped,
        )


def _map_cards(raw_cards: list[object]) -> tuple[list[OptcgCardCreate], int]:
    cards: list[OptcgCardCreate] = []
    invalid = 0
    for item in raw_cards:
        if not isinstance(item, dict):
            invalid += 1
            continue
        try:
            cards.append(to_card_create(item))
        except (PydanticValidationError, ValidationError):
            invalid += 1
    return cards, invalid


async def _emit(on_progress: ProgressCallback | None, message: str) -> None:
    if on_progress is None:
        return
    await on_progress(message)
