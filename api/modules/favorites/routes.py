"""HTTP routes for starred cards and products."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import FavoriteServiceDep
from .schemas import FavoriteCreate, FavoriteIds, FavoriteRead

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get(
    "/ids",
    response_model=FavoriteIds,
    summary="List starred catalog ids",
    responses={401: {"description": "Not authenticated"}},
)
async def list_favorite_ids(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    favorites: FavoriteServiceDep,
) -> FavoriteIds:
    """Return card and product ids the current user has starred."""
    return await favorites.list_ids(db, current_user["id"])


@router.get(
    "",
    response_model=PaginatedListResponse[FavoriteRead],
    summary="List favorites",
    responses={401: {"description": "Not authenticated"}},
)
async def list_favorites(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    favorites: FavoriteServiceDep,
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    """Return a paginated favorites page with catalog display fields."""
    data = await favorites.list_paginated(
        db,
        current_user["id"],
        skip=compute_offset(page, items_per_page),
        limit=items_per_page,
    )
    return paginated_response(crud_data=data, page=page, items_per_page=items_per_page)


@router.post(
    "",
    status_code=201,
    response_model=FavoriteRead,
    summary="Star a card or product",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Card or product not found"},
    },
)
async def add_favorite(
    payload: FavoriteCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    favorites: FavoriteServiceDep,
) -> FavoriteRead:
    """Idempotently star a catalog item."""
    return await favorites.add(db, current_user["id"], payload)


@router.delete(
    "/cards/{card_id}",
    status_code=204,
    summary="Unstar a card",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Favorite not found"},
    },
)
async def remove_card_favorite(
    card_id: int,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    favorites: FavoriteServiceDep,
) -> None:
    """Remove a card favorite without knowing its UUID."""
    await favorites.remove_card(db, current_user["id"], card_id)


@router.delete(
    "/products/{product_id}",
    status_code=204,
    summary="Unstar a product",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Favorite not found"},
    },
)
async def remove_product_favorite(
    product_id: int,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    favorites: FavoriteServiceDep,
) -> None:
    """Remove a product favorite without knowing its UUID."""
    await favorites.remove_product(db, current_user["id"], product_id)


@router.delete(
    "/{favorite_id}",
    status_code=204,
    summary="Unstar by favorite id",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Favorite not found"},
    },
)
async def remove_favorite(
    favorite_id: UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    favorites: FavoriteServiceDep,
) -> None:
    """Remove a favorite by its id."""
    await favorites.remove(db, current_user["id"], favorite_id)
