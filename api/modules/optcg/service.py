from typing import Any

from sqlalchemy import ColumnElement, func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select

from fastcrud.types import GetMultiResponseDict

from ..cards.enums import CardGame
from ..cards.models import Card
from .models import OptcgCard
from .schemas import OptcgCardCreate, OptcgCardFilterOptions, OptcgCardSort

SET_FILTER_EXCLUDED_WORDS = ("starter", "release", "cards")
BASE_NAME_PAREN_PATTERN = r"\([^)]+\)"

INSERT_BATCH_SIZE = 500


class OptcgCatalogService:
    """Persistence for the OPTCG catalog (shared identity + game detail)."""

    async def bulk_insert_missing(
        self,
        cards: list[OptcgCardCreate],
        db: AsyncSession,
    ) -> tuple[int, int]:
        """Insert cards that do not already exist for the same name and set.

        Skips rows whose `(game, name, set_name)` is already in the catalog
        or duplicated within the incoming payload. Writes a `card` row and an
        `optcg_card` detail row in the same transaction.

        Args:
            cards: Mapped catalog cards to consider for insert.
            db: Database session for the operation.

        Returns:
            A tuple of `(inserted, skipped)` counts.
        """
        result = await db.execute(
            select(Card.name, Card.set_name, Card.tcgplayer_id).where(Card.game == CardGame.OPTCG.value)
        )
        rows = result.all()
        existing = {(row.name, row.set_name) for row in rows}
        existing_ids = {row.tcgplayer_id for row in rows}

        to_insert: list[OptcgCardCreate] = []
        skipped = 0
        seen_in_payload: set[tuple[str, str]] = set()
        seen_ids: set[int] = set()

        for card in cards:
            key = (card.card_name, card.set_name)
            if (
                key in existing
                or key in seen_in_payload
                or card.tcgplayer_id in existing_ids
                or card.tcgplayer_id in seen_ids
            ):
                skipped += 1
                continue
            seen_in_payload.add(key)
            seen_ids.add(card.tcgplayer_id)
            existing.add(key)
            existing_ids.add(card.tcgplayer_id)
            to_insert.append(card)

        for offset in range(0, len(to_insert), INSERT_BATCH_SIZE):
            batch = to_insert[offset : offset + INSERT_BATCH_SIZE]
            identities: list[tuple[Card, OptcgCardCreate]] = []
            for source in batch:
                identity = Card(
                    game=CardGame.OPTCG.value,
                    name=source.card_name,
                    set_name=source.set_name,
                    tcgplayer_id=source.tcgplayer_id,
                    card_number=source.card_set_id,
                    rarity=source.rarity,
                    card_type=source.card_type,
                    image_url=source.card_image,
                )
                db.add(identity)
                identities.append((identity, source))
            await db.flush()
            db.add_all(
                [
                    OptcgCard(
                        card_id=identity.id,
                        date_scraped=source.date_scraped,
                        card_text=source.card_text,
                        card_color=source.card_color,
                        life=source.life,
                        card_cost=source.card_cost,
                        card_power=source.card_power,
                        sub_types=source.sub_types,
                        counter_amount=source.counter_amount,
                        attribute=source.attribute,
                    )
                    for identity, source in identities
                ]
            )
            await db.flush()

        await db.commit()
        return len(to_insert), skipped

    async def list_paginated(
        self,
        db: AsyncSession,
        skip: int,
        limit: int,
        colors: list[str] | None = None,
        rarities: list[str] | None = None,
        set_names: list[str] | None = None,
        name: str | None = None,
        base_only: bool = False,
        sort: OptcgCardSort = "set",
    ) -> GetMultiResponseDict:
        """Return a page of OPTCG catalog cards, optionally filtered."""
        filters = _optcg_filters(
            colors=colors,
            rarities=rarities,
            set_names=set_names,
            name=name,
            base_only=base_only,
        )

        count_stmt = select(func.count()).select_from(Card).join(OptcgCard).where(*filters)
        total = int((await db.execute(count_stmt)).scalar_one())

        stmt = (
            select(
                Card.id,
                Card.name,
                Card.card_number,
                Card.rarity,
                Card.image_url,
            )
            .join(OptcgCard)
            .where(*filters)
            .order_by(*_optcg_order(sort))
            .offset(skip)
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()
        return {
            "data": [
                {
                    "id": row.id,
                    "card_name": row.name,
                    "card_set_id": row.card_number,
                    "rarity": row.rarity,
                    "card_image": row.image_url,
                }
                for row in rows
            ],
            "total_count": total,
        }

    async def list_filter_options(self, db: AsyncSession) -> OptcgCardFilterOptions:
        """Return distinct color, rarity, and set name values for filters."""
        return OptcgCardFilterOptions(
            colors=await _distinct_optcg_colors(db),
            rarities=await _distinct_card_values(db, Card.rarity),
            set_names=_catalog_set_names(await _distinct_card_values(db, Card.set_name)),
        )


def _ilike_contains(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _clean_values(values: list[str] | None) -> list[str]:
    return [value.strip() for value in values or [] if value.strip()]


def _catalog_set_names(names: list[str]) -> list[str]:
    return [
        name
        for name in names
        if not any(word in name.lower() for word in SET_FILTER_EXCLUDED_WORDS)
    ]


def _optcg_order(sort: OptcgCardSort) -> tuple[ColumnElement[Any], ...]:
    if sort == "number":
        return (Card.card_number.asc(),)
    if sort == "number_desc":
        return (Card.card_number.desc(),)
    return (Card.set_name.asc(), Card.card_number.asc())


def _optcg_filters(
    colors: list[str] | None = None,
    rarities: list[str] | None = None,
    set_names: list[str] | None = None,
    name: str | None = None,
    base_only: bool = False,
) -> list[ColumnElement[bool]]:
    filters: list[ColumnElement[bool]] = [Card.game == CardGame.OPTCG.value]
    cleaned_colors = _clean_values(colors)
    cleaned_rarities = _clean_values(rarities)
    cleaned_set_names = _clean_values(set_names)
    if cleaned_colors:
        filters.append(OptcgCard.card_color.in_(cleaned_colors))
    if cleaned_rarities:
        filters.append(Card.rarity.in_(cleaned_rarities))
    if cleaned_set_names:
        filters.append(Card.set_name.in_(cleaned_set_names))
    if name:
        filters.append(Card.name.ilike(_ilike_contains(name), escape="\\"))
    if base_only:
        filters.append(not_(Card.name.op("~")(BASE_NAME_PAREN_PATTERN)))
    return filters


async def _distinct_optcg_colors(db: AsyncSession) -> list[str]:
    column = OptcgCard.card_color
    result = await db.execute(select(column).where(column.is_not(None)).distinct().order_by(column))
    return [value for value in result.scalars().all() if value]


async def _distinct_card_values(db: AsyncSession, column: InstrumentedAttribute[Any]) -> list[str]:
    stmt: Select = (
        select(column)
        .where(Card.game == CardGame.OPTCG.value, column.is_not(None))
        .distinct()
        .order_by(column)
    )
    result = await db.execute(stmt)
    return [value for value in result.scalars().all() if value]
