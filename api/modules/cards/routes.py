"""HTTP routes for the shared card catalog."""

from typing import Any

from fastapi import APIRouter, Query
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import CardCatalogServiceDep
from .enums import CardGame
from .schemas import CardFilterOptions, CardListItem, CardRead
from .service import as_game_value

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get(
    "/filters",
    response_model=CardFilterOptions,
    summary="List shared catalog filter options",
    description="Returns distinct rarity and set name values. Optionally scoped to one game.",
    responses={401: {"description": "Not authenticated"}},
)
async def get_card_filters(
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: CardCatalogServiceDep,
    game: CardGame | None = Query(default=None),
) -> CardFilterOptions:
    """Return distinct values for shared catalog list filters."""
    return await catalog.list_filter_options(db, game=as_game_value(game))


@router.get(
    "/{card_id}",
    response_model=CardRead,
    summary="Get a shared catalog card",
    description="Returns one identity row by canonical card id.",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Card not found"},
    },
)
async def get_card(
    card_id: int,
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: CardCatalogServiceDep,
) -> CardRead:
    """Return one shared catalog card."""
    return await catalog.get_by_id(db, card_id)


@router.get(
    "",
    response_model=PaginatedListResponse[CardListItem],
    summary="List shared catalog cards",
    description="Returns a paginated identity page. Filter by game, rarity, or set name.",
    responses={401: {"description": "Not authenticated"}},
)
async def list_cards(
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: CardCatalogServiceDep,
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=50, ge=1, le=100),
    game: CardGame | None = Query(default=None),
    rarity: str | None = Query(default=None),
    set_name: str | None = Query(default=None),
) -> dict[str, Any]:
    """Return a paginated list of shared catalog cards."""
    cards_data = await catalog.list_paginated(
        db=db,
        skip=compute_offset(page, items_per_page),
        limit=items_per_page,
        game=as_game_value(game),
        rarity=rarity.strip() if rarity else None,
        set_name=set_name.strip() if set_name else None,
    )
    return paginated_response(crud_data=cards_data, page=page, items_per_page=items_per_page)
