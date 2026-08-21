from typing import Any

from fastcrud.types import GetMultiResponseDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from .crud import crud_optcg_cards
from .models import OptcgCard
from .schemas import OptcgCardCreate, OptcgCardFilterOptions, OptcgCardListItem

INSERT_BATCH_SIZE = 500


class OptcgCatalogService:
    """Persistence for the shared OPTCG card catalog."""

    async def bulk_insert_missing(
        self,
        cards: list[OptcgCardCreate],
        db: AsyncSession,
    ) -> tuple[int, int]:
        """Insert cards that do not already exist for the same name and set.

        Skips rows whose `(card_name, set_id)` is already in the catalog or
        duplicated within the incoming payload.

        Args:
            cards: Mapped catalog cards to consider for insert.
            db: Database session for the operation.

        Returns:
            A tuple of `(inserted, skipped)` counts.
        """
        result = await db.execute(select(OptcgCard.card_name, OptcgCard.set_id))
        existing = {(row.card_name, row.set_id) for row in result.all()}

        to_insert: list[OptcgCardCreate] = []
        skipped = 0
        seen_in_payload: set[tuple[str, str]] = set()

        for card in cards:
            key = (card.card_name, card.set_id)
            if key in existing or key in seen_in_payload:
                skipped += 1
                continue
            seen_in_payload.add(key)
            existing.add(key)
            to_insert.append(card)

        for offset in range(0, len(to_insert), INSERT_BATCH_SIZE):
            batch = to_insert[offset : offset + INSERT_BATCH_SIZE]
            db.add_all([OptcgCard(**card.model_dump()) for card in batch])
            await db.flush()

        await db.commit()
        return len(to_insert), skipped

    async def list_paginated(
        self,
        db: AsyncSession,
        skip: int,
        limit: int,
        color: str | None = None,
        rarity: str | None = None,
        set_name: str | None = None,
    ) -> GetMultiResponseDict:
        """Return a page of catalog cards, optionally filtered."""
        filters: dict[str, str] = {}
        if color:
            filters["card_color"] = color
        if rarity:
            filters["rarity"] = rarity
        if set_name:
            filters["set_name"] = set_name

        return await crud_optcg_cards.get_multi(
            db=db,
            offset=skip,
            limit=limit,
            schema_to_select=OptcgCardListItem,
            sort_columns=["set_id", "card_set_id"],
            sort_orders=["asc", "asc"],
            **filters,
        )

    async def list_filter_options(self, db: AsyncSession) -> OptcgCardFilterOptions:
        """Return distinct color, rarity, and set name values for filters."""
        return OptcgCardFilterOptions(
            colors=await _distinct_values(db, OptcgCard.card_color),
            rarities=await _distinct_values(db, OptcgCard.rarity),
            set_names=await _distinct_values(db, OptcgCard.set_name),
        )


async def _distinct_values(db: AsyncSession, column: InstrumentedAttribute[Any]) -> list[str]:
    result = await db.execute(select(column).where(column.is_not(None)).distinct().order_by(column))
    return [value for value in result.scalars().all() if value]
