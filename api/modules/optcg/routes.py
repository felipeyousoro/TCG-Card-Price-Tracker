"""HTTP routes for the OPTCG card catalog."""

from typing import Any

from fastapi import APIRouter, Query
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import OptcgCatalogServiceDep
from .schemas import OptcgCardFilterOptions, OptcgCardListItem

router = APIRouter(prefix="/optcg", tags=["OPTCG"])


@router.get(
    "/cards/filters",
    response_model=OptcgCardFilterOptions,
    summary="List OPTCG filter options",
    description="Returns distinct color, rarity, and set name values for catalog filters.",
    responses={401: {"description": "Not authenticated"}},
)
async def get_card_filters(
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: OptcgCatalogServiceDep,
) -> OptcgCardFilterOptions:
    """Return distinct values for catalog list filters."""
    return await catalog.list_filter_options(db)


@router.get(
    "/cards",
    response_model=PaginatedListResponse[OptcgCardListItem],
    summary="List OPTCG cards",
    description="Returns a paginated catalog page. Filter by exact color, rarity, or set name.",
    responses={401: {"description": "Not authenticated"}},
)
async def list_cards(
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: OptcgCatalogServiceDep,
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=50, ge=1, le=100),
    color: str | None = Query(default=None),
    rarity: str | None = Query(default=None),
    set_name: str | None = Query(default=None),
) -> dict[str, Any]:
    """Return a paginated list of OPTCG catalog cards."""
    cards_data = await catalog.list_paginated(
        db=db,
        skip=compute_offset(page, items_per_page),
        limit=items_per_page,
        color=color.strip() if color else None,
        rarity=rarity.strip() if rarity else None,
        set_name=set_name.strip() if set_name else None,
    )
    return paginated_response(crud_data=cards_data, page=page, items_per_page=items_per_page)
