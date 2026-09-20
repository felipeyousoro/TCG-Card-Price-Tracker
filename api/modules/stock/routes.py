"""HTTP routes for holdings and buy history."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query
from fastcrud import PaginatedListResponse, compute_offset, paginated_response

from ...core.dependencies import AsyncSessionDep, CurrentUserDep
from .dependencies import StockServiceDep
from .schemas import (
    BuyCardRequest,
    BuyProductRequest,
    HoldingItem,
    ImportPreviewRequest,
    ImportPreviewResult,
    SellRequest,
    StockQuantities,
    TransactionCreate,
    TransactionRead,
)

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get(
    "/quantities",
    response_model=StockQuantities,
    summary="Owned quantities by catalog id",
    responses={401: {"description": "Not authenticated"}},
)
async def get_quantities(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> StockQuantities:
    """Return a compact map of owned card and product quantities."""
    return await stock.list_quantities(db, current_user["id"])


@router.get(
    "/transactions",
    response_model=PaginatedListResponse[TransactionRead],
    summary="List buy history",
    responses={401: {"description": "Not authenticated"}},
)
async def list_transactions(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """Return paginated transaction headers with lines."""
    data = await stock.list_transactions(
        db,
        current_user["id"],
        skip=compute_offset(page, items_per_page),
        limit=items_per_page,
    )
    return paginated_response(crud_data=data, page=page, items_per_page=items_per_page)


@router.post(
    "/transactions/import/preview",
    response_model=ImportPreviewResult,
    summary="Preview pasted buy lines without writing stock",
    responses={401: {"description": "Not authenticated"}},
)
async def preview_import_transactions(
    payload: ImportPreviewRequest,
    db: AsyncSessionDep,
    _current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> ImportPreviewResult:
    """Resolve pasted semicolon-separated lines to catalog cards."""
    return await stock.preview_import(db, payload.text)


@router.post(
    "/transactions",
    status_code=201,
    response_model=TransactionRead,
    summary="Record a multi-line buy",
    responses={401: {"description": "Not authenticated"}},
)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> TransactionRead:
    """Create one buy header with many lines."""
    return await stock.create_transaction(db, current_user["id"], payload)


@router.delete(
    "/transactions/{transaction_id}",
    status_code=204,
    summary="Delete a buy and reverse holdings",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Transaction not found"},
    },
)
async def delete_transaction(
    transaction_id: UUID,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> None:
    """Remove a buy order and undo its effect on aggregates."""
    await stock.delete_transaction(db, current_user["id"], transaction_id)


@router.post(
    "/cards/{card_id}/buy",
    status_code=201,
    response_model=TransactionRead,
    summary="Record a single-card buy",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Card not found"},
    },
)
async def buy_card(
    card_id: int,
    payload: BuyCardRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> TransactionRead:
    """Record a one-line card purchase."""
    return await stock.buy_card(db, current_user["id"], card_id, payload)


@router.post(
    "/products/{product_id}/buy",
    status_code=201,
    response_model=TransactionRead,
    summary="Record a single-product buy",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Product not found"},
    },
)
async def buy_product(
    product_id: int,
    payload: BuyProductRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> TransactionRead:
    """Record a one-line product purchase."""
    return await stock.buy_product(db, current_user["id"], product_id, payload)


@router.post(
    "/cards/{card_id}/sell",
    status_code=201,
    response_model=TransactionRead,
    summary="Record a single-card sell",
    responses={
        400: {"description": "Not enough quantity to sell"},
        401: {"description": "Not authenticated"},
        404: {"description": "Card not found"},
    },
)
async def sell_card(
    card_id: int,
    payload: SellRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> TransactionRead:
    """Record a one-line card sale against current average cost."""
    return await stock.sell_card(db, current_user["id"], card_id, payload)


@router.post(
    "/products/{product_id}/sell",
    status_code=201,
    response_model=TransactionRead,
    summary="Record a single-product sell",
    responses={
        400: {"description": "Not enough quantity to sell"},
        401: {"description": "Not authenticated"},
        404: {"description": "Product not found"},
    },
)
async def sell_product(
    product_id: int,
    payload: SellRequest,
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
) -> TransactionRead:
    """Record a one-line product sale against current average cost."""
    return await stock.sell_product(db, current_user["id"], product_id, payload)


@router.get(
    "",
    response_model=PaginatedListResponse[HoldingItem],
    summary="List current holdings",
    responses={401: {"description": "Not authenticated"}},
)
async def list_holdings(
    db: AsyncSessionDep,
    current_user: CurrentUserDep,
    stock: StockServiceDep,
    page: int = Query(default=1, ge=1),
    items_per_page: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    """Return paginated card and product holdings."""
    data = await stock.list_holdings(
        db,
        current_user["id"],
        skip=compute_offset(page, items_per_page),
        limit=items_per_page,
    )
    return paginated_response(crud_data=data, page=page, items_per_page=items_per_page)
