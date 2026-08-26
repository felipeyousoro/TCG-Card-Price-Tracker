import asyncio

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ....common.exceptions import ImporterFetchError, ValidationError
from ....modules.optcg.schemas import OptcgCardCreate
from ....modules.optcg.service import OptcgCatalogService
from ..base import ImportResult, ProgressCallback
from .api.tcgcsv.client import TcgcsvClient
from .api.tcgcsv.mapper import to_card_create
from .groups import TcgplayerGroup, load_optcg_groups

GROUP_FETCH_CONCURRENCY = 3


class TcgcsvImporter:
    """Loads OPTCG catalog cards from tcgcsv.com into the shared domain."""

    source = "tcgcsv"

    def __init__(self, client: TcgcsvClient, catalog: OptcgCatalogService) -> None:
        self._client = client
        self._catalog = catalog

    async def import_all_sets(
        self,
        db: AsyncSession,
        *,
        on_progress: ProgressCallback | None = None,
        group_ids: list[int] | None = None,
    ) -> ImportResult:
        """Fetch TCGCSV products for selected or all enabled groups and insert missing rows."""
        groups = resolve_groups(group_ids)
        if not groups:
            raise ValidationError("No TCGPlayer groups are enabled for import")

        await _emit(on_progress, f"Fetching {len(groups)} TCGCSV group(s)")
        fetched_groups = await _fetch_groups(self._client, groups, on_progress=on_progress)
        if not fetched_groups:
            raise ImporterFetchError("Failed to fetch TCGCSV products for every selected group")

        fetched = 0
        inserted = 0
        skipped = 0
        for group, raw_products in fetched_groups:
            await _emit(on_progress, f"Mapping {len(raw_products)} products from {group.name}")
            cards, invalid = await asyncio.to_thread(_map_products, raw_products, group.name)
            fetched += len(raw_products)
            skipped += invalid
            if invalid:
                await _emit(on_progress, f"Skipped {invalid} invalid payloads in {group.name}")
            await _emit(on_progress, f"Inserting missing catalog rows for {group.name}")
            group_inserted, group_skipped = await self._catalog.bulk_insert_missing(cards, db)
            inserted += group_inserted
            skipped += group_skipped

        failed = len(groups) - len(fetched_groups)
        if failed:
            await _emit(
                on_progress,
                f"Finished with {failed} group fetch failure(s); inserted={inserted} skipped={skipped}",
            )

        return ImportResult(
            source=self.source,
            fetched=fetched,
            inserted=inserted,
            skipped=skipped,
        )


def resolve_groups(group_ids: list[int] | None) -> list[TcgplayerGroup]:
    catalog = load_optcg_groups()
    if group_ids is None:
        return [group for group in catalog if group.enabled]

    wanted = list(dict.fromkeys(group_ids))
    by_id = {group.group_id: group for group in catalog}
    missing = [group_id for group_id in wanted if group_id not in by_id]
    if missing:
        raise ValidationError(f"Unknown TCGPlayer group id(s): {', '.join(str(item) for item in missing)}")
    return [by_id[group_id] for group_id in wanted]


async def _fetch_groups(
    client: TcgcsvClient,
    groups: list[TcgplayerGroup],
    *,
    on_progress: ProgressCallback | None,
) -> list[tuple[TcgplayerGroup, list[dict[str, object]]]]:
    semaphore = asyncio.Semaphore(GROUP_FETCH_CONCURRENCY)

    async def fetch_one(
        group: TcgplayerGroup,
    ) -> tuple[TcgplayerGroup, list[dict[str, object]] | None, str | None]:
        async with semaphore:
            await _emit(on_progress, f"Fetching {group.name} ({group.group_id})")
            try:
                products = await client.fetch_products(group.category_id, group.group_id)
            except (ImporterFetchError, ValidationError) as exc:
                return group, None, str(exc).strip() or type(exc).__name__
            return group, products, None

    outcomes = await asyncio.gather(*[fetch_one(group) for group in groups])
    succeeded: list[tuple[TcgplayerGroup, list[dict[str, object]]]] = []
    for group, products, error in outcomes:
        if products is None:
            await _emit(on_progress, f"Failed {group.name} ({group.group_id}): {error}")
            continue
        await _emit(on_progress, f"Fetched {len(products)} products from {group.name}")
        succeeded.append((group, products))
    return succeeded


def _map_products(raw_products: list[object], set_name: str) -> tuple[list[OptcgCardCreate], int]:
    cards: list[OptcgCardCreate] = []
    invalid = 0
    for item in raw_products:
        if not isinstance(item, dict):
            invalid += 1
            continue
        try:
            cards.append(to_card_create(item, set_name))
        except (PydanticValidationError, ValidationError):
            invalid += 1
    return cards, invalid


async def _emit(on_progress: ProgressCallback | None, message: str) -> None:
    if on_progress is None:
        return
    await on_progress(message)
