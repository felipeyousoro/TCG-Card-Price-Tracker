from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ....common.exceptions import ValidationError
from ....modules.optcg.service import OptcgCatalogService
from ..base import ImportResult
from .client import OptcgApiClient
from .mapper import to_card_create


class OptcgApiImporter:
    """Loads OPTCG catalog cards from optcgapi.com into the shared domain."""

    source = "optcgapi"

    def __init__(self, client: OptcgApiClient, catalog: OptcgCatalogService) -> None:
        self._client = client
        self._catalog = catalog

    async def import_all_sets(self, db: AsyncSession) -> ImportResult:
        """Fetch all set cards, map them, and insert missing catalog rows."""
        raw_cards = await self._client.fetch_all_set_cards()
        cards = []
        for item in raw_cards:
            if not isinstance(item, dict):
                raise ValidationError("optcgapi allSetCards items must be objects")
            try:
                cards.append(to_card_create(item))
            except PydanticValidationError as exc:
                raise ValidationError("Invalid card payload from optcgapi") from exc

        inserted, skipped = await self._catalog.bulk_insert_missing(cards, db)
        return ImportResult(
            source=self.source,
            fetched=len(raw_cards),
            inserted=inserted,
            skipped=skipped,
        )
