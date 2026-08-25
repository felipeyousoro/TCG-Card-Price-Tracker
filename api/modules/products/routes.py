"""HTTP routes for the shared product catalog."""

from typing import Any

from fastapi import APIRouter, Query
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import ProductCatalogServiceDep
from .schemas import ProductCreate, ProductListItem, ProductRead

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=PaginatedListResponse[ProductListItem],
    summary="Search products",
    description="Paginated catalog search. Filter by name with case-insensitive ILIKE.",
    responses={401: {"description": "Not authenticated"}},
)
async def list_products(
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: ProductCatalogServiceDep,
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
) -> dict[str, Any]:
    """Return a paginated product list."""
    data = await catalog.list_paginated(
        db=db,
        skip=compute_offset(page, items_per_page),
        limit=items_per_page,
        q=q,
    )
    return paginated_response(crud_data=data, page=page, items_per_page=items_per_page)


@router.post(
    "",
    status_code=201,
    response_model=ProductRead,
    summary="Create a product",
    description="Adds a shared catalog product. Any user may later buy against it.",
    responses={401: {"description": "Not authenticated"}},
)
async def create_product(
    payload: ProductCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    catalog: ProductCatalogServiceDep,
) -> ProductRead:
    """Create a shared product catalog row."""
    return await catalog.create(db, payload, user_id=current_user["id"])


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get a product",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Product not found"},
    },
)
async def get_product(
    product_id: int,
    db: AsyncSessionDep,
    _: CurrentUserDep,
    catalog: ProductCatalogServiceDep,
) -> ProductRead:
    """Return one catalog product."""
    return await catalog.get_by_id(db, product_id)
