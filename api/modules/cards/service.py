from typing import Any

from fastcrud.types import GetMultiResponseDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from ...core.auth.http_exceptions import NotFoundException
from .crud import crud_cards
from .enums import CardGame
from .models import Card
from .schemas import CardFilterOptions, CardListItem, CardRead


class CardCatalogService:
    """Persistence for the shared card identity table."""

    async def list_paginated(
        self,
        db: AsyncSession,
        skip: int,
        limit: int,
        game: str | None = None,
        rarity: str | None = None,
        set_name: str | None = None,
    ) -> GetMultiResponseDict:
        """Return a page of shared catalog cards, optionally filtered."""
        filters: dict[str, str] = {}
        if game:
            filters["game"] = game
        if rarity:
            filters["rarity"] = rarity
        if set_name:
            filters["set_name"] = set_name

        return await crud_cards.get_multi(
            db=db,
            offset=skip,
            limit=limit,
            schema_to_select=CardListItem,
            sort_columns=["set_code", "card_number"],
            sort_orders=["asc", "asc"],
            **filters,
        )

    async def get_by_id(self, db: AsyncSession, card_id: int) -> CardRead:
        """Return one shared catalog card or raise if it does not exist."""
        card = await crud_cards.get(db=db, id=card_id, schema_to_select=CardRead)
        if not card:
            raise NotFoundException(detail="Card not found")
        return card

    async def list_filter_options(
        self,
        db: AsyncSession,
        game: str | None = None,
    ) -> CardFilterOptions:
        """Return distinct rarity and set name values for the shared catalog."""
        return CardFilterOptions(
            rarities=await _distinct_values(db, Card.rarity, game=game),
            set_names=await _distinct_values(db, Card.set_name, game=game),
        )


async def _distinct_values(
    db: AsyncSession,
    column: InstrumentedAttribute[Any],
    game: str | None = None,
) -> list[str]:
    stmt = select(column).where(column.is_not(None)).distinct().order_by(column)
    if game:
        stmt = stmt.where(Card.game == game)
    result = await db.execute(stmt)
    return [value for value in result.scalars().all() if value]


def as_game_value(game: CardGame | None) -> str | None:
    """Return the stored string for a game filter, if any."""
    return game.value if game else None
