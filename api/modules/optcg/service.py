from typing import Any

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select

from fastcrud.types import GetMultiResponseDict

from ..cards.enums import CardGame
from ..cards.models import Card
from .models import OptcgCard
from .schemas import OptcgCardCreate, OptcgCardFilterOptions

INSERT_BATCH_SIZE = 500


class OptcgCatalogService:
    """Persistence for the OPTCG catalog (shared identity + game detail)."""

    async def bulk_insert_missing(
        self,
        cards: list[OptcgCardCreate],
        db: AsyncSession,
    ) -> tuple[int, int]:
        """Insert cards that do not already exist for the same name and set.

        Skips rows whose `(game, name, set_code)` is already in the catalog
        or duplicated within the incoming payload. Writes a `card` row and an
        `optcg_card` detail row in the same transaction.

        Args:
            cards: Mapped catalog cards to consider for insert.
            db: Database session for the operation.

        Returns:
            A tuple of `(inserted, skipped)` counts.
        """
        result = await db.execute(
            select(Card.name, Card.set_code).where(Card.game == CardGame.OPTCG.value)
        )
        existing = {(row.name, row.set_code) for row in result.all()}

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
            identities: list[tuple[Card, OptcgCardCreate]] = []
            for source in batch:
                identity = Card(
                    game=CardGame.OPTCG.value,
                    name=source.card_name,
                    set_name=source.set_name,
                    set_code=source.set_id,
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
                        card_image_id=source.card_image_id,
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
        color: str | None = None,
        rarity: str | None = None,
        set_name: str | None = None,
    ) -> GetMultiResponseDict:
        """Return a page of OPTCG catalog cards, optionally filtered."""
        filters = _optcg_filters(color=color, rarity=rarity, set_name=set_name)

        count_stmt = select(func.count()).select_from(Card).join(OptcgCard).where(*filters)
        total = int((await db.execute(count_stmt)).scalar_one())

        stmt = (
            select(
                Card.id,
                Card.name,
                Card.card_number,
                Card.image_url,
            )
            .join(OptcgCard)
            .where(*filters)
            .order_by(Card.set_code.asc(), Card.card_number.asc())
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
            set_names=await _distinct_card_values(db, Card.set_name),
        )


def _optcg_filters(
    color: str | None = None,
    rarity: str | None = None,
    set_name: str | None = None,
) -> list[ColumnElement[bool]]:
    filters: list[ColumnElement[bool]] = [Card.game == CardGame.OPTCG.value]
    if color:
        filters.append(OptcgCard.card_color == color)
    if rarity:
        filters.append(Card.rarity == rarity)
    if set_name:
        filters.append(Card.set_name == set_name)
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
