from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import Integer, cast, func, literal, null, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth.http_exceptions import BadRequestException
from ..cards.models import Card
from ..products.models import Product
from ..stock.enums import ItemType, TransactionType
from ..stock.models import InventoryTransaction, StockTransaction, UserCardStock, UserProductStock
from .schemas import (
    DashboardByItem,
    DashboardHoldingRank,
    DashboardItemGain,
    DashboardSeries,
    DashboardSeriesPoint,
    DashboardSummary,
)

TWOPLACES = Decimal("0.01")


class DashboardService:
    """Aggregate buy/sell cash and current holdings for P&L views."""

    async def get_summary(
        self,
        db: AsyncSession,
        user_id: int,
        date_from: date | None,
        date_to: date | None,
    ) -> DashboardSummary:
        _validate_range(date_from, date_to)
        invested, proceeds, realized = await _period_totals(db, user_id, date_from, date_to)
        holdings_count, remaining_cost = await _current_holdings_metrics(db, user_id)
        return DashboardSummary(
            date_from=date_from,
            date_to=date_to,
            total_invested=float(invested),
            total_proceeds=float(proceeds),
            realized_pnl=float(realized),
            holdings_count=holdings_count,
            remaining_cost_basis=float(remaining_cost),
        )

    async def get_series(
        self,
        db: AsyncSession,
        user_id: int,
        date_from: date | None,
        date_to: date | None,
    ) -> DashboardSeries:
        start, end = await _resolve_series_range(db, user_id, date_from, date_to)
        spend_by_day, pnl_by_day = await _daily_totals(db, user_id, start, end)
        points: list[DashboardSeriesPoint] = []
        cursor = start
        while cursor <= end:
            points.append(
                DashboardSeriesPoint(
                    date=cursor,
                    buy_spend=float(spend_by_day.get(cursor, Decimal("0")).quantize(TWOPLACES)),
                    realized_pnl=float(pnl_by_day.get(cursor, Decimal("0")).quantize(TWOPLACES)),
                )
            )
            cursor += timedelta(days=1)
        return DashboardSeries(date_from=start, date_to=end, points=points)

    async def get_by_item(
        self,
        db: AsyncSession,
        user_id: int,
        date_from: date | None,
        date_to: date | None,
        limit: int,
    ) -> DashboardByItem:
        _validate_range(date_from, date_to)
        realized_rows = await _realized_by_item(db, user_id, date_from, date_to)
        best = realized_rows[:limit]
        worst = sorted(realized_rows, key=lambda item: (item.realized_gain, item.name))[:limit]
        top_holdings = await _top_holdings(db, user_id, limit)
        return DashboardByItem(
            date_from=date_from,
            date_to=date_to,
            best_realized=best,
            worst_realized=worst,
            top_holdings=top_holdings,
        )


def _validate_range(date_from: date | None, date_to: date | None) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise BadRequestException(detail="date_from must be on or before date_to")


async def _resolve_series_range(
    db: AsyncSession,
    user_id: int,
    date_from: date | None,
    date_to: date | None,
) -> tuple[date, date]:
    _validate_range(date_from, date_to)
    today = datetime.now(UTC).date()
    end = date_to or today
    if date_from is not None:
        return date_from, end
    min_date = (
        await db.execute(
            select(func.min(InventoryTransaction.transaction_date)).where(
                InventoryTransaction.user_id == user_id
            )
        )
    ).scalar_one()
    start = min_date or end
    if start > end:
        raise BadRequestException(detail="date_from must be on or before date_to")
    return start, end


def _apply_date_filters(stmt, date_from: date | None, date_to: date | None):
    if date_from is not None:
        stmt = stmt.where(InventoryTransaction.transaction_date >= date_from)
    if date_to is not None:
        stmt = stmt.where(InventoryTransaction.transaction_date <= date_to)
    return stmt


async def _period_totals(
    db: AsyncSession,
    user_id: int,
    date_from: date | None,
    date_to: date | None,
) -> tuple[Decimal, Decimal, Decimal]:
    stmt = (
        select(
            InventoryTransaction.transaction_type,
            func.coalesce(func.sum(StockTransaction.line_total), 0),
            func.coalesce(func.sum(StockTransaction.realized_gain), 0),
        )
        .join(StockTransaction, StockTransaction.transaction_id == InventoryTransaction.id)
        .where(InventoryTransaction.user_id == user_id)
        .group_by(InventoryTransaction.transaction_type)
    )
    stmt = _apply_date_filters(stmt, date_from, date_to)
    invested = Decimal("0")
    proceeds = Decimal("0")
    realized = Decimal("0")
    for row in (await db.execute(stmt)).all():
        txn_type, line_total, gain = row
        amount = Decimal(line_total)
        if txn_type == TransactionType.BUY.value:
            invested = amount
        elif txn_type == TransactionType.SELL.value:
            proceeds = amount
            realized = Decimal(gain)
    return invested.quantize(TWOPLACES), proceeds.quantize(TWOPLACES), realized.quantize(TWOPLACES)


async def _current_holdings_metrics(db: AsyncSession, user_id: int) -> tuple[int, Decimal]:
    card_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(UserCardStock)
                .where(UserCardStock.user_id == user_id, UserCardStock.quantity > 0)
            )
        ).scalar_one()
    )
    product_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(UserProductStock)
                .where(UserProductStock.user_id == user_id, UserProductStock.quantity > 0)
            )
        ).scalar_one()
    )
    card_cost = (
        await db.execute(
            select(func.coalesce(func.sum(UserCardStock.quantity * UserCardStock.avg_unit_cost), 0)).where(
                UserCardStock.user_id == user_id,
                UserCardStock.quantity > 0,
            )
        )
    ).scalar_one()
    product_cost = (
        await db.execute(
            select(
                func.coalesce(func.sum(UserProductStock.quantity * UserProductStock.avg_unit_cost), 0)
            ).where(
                UserProductStock.user_id == user_id,
                UserProductStock.quantity > 0,
            )
        )
    ).scalar_one()
    remaining = (Decimal(card_cost) + Decimal(product_cost)).quantize(TWOPLACES)
    return card_count + product_count, remaining


async def _daily_totals(
    db: AsyncSession,
    user_id: int,
    start: date,
    end: date,
) -> tuple[dict[date, Decimal], dict[date, Decimal]]:
    stmt = (
        select(
            InventoryTransaction.transaction_date,
            InventoryTransaction.transaction_type,
            func.coalesce(func.sum(StockTransaction.line_total), 0),
            func.coalesce(func.sum(StockTransaction.realized_gain), 0),
        )
        .join(StockTransaction, StockTransaction.transaction_id == InventoryTransaction.id)
        .where(
            InventoryTransaction.user_id == user_id,
            InventoryTransaction.transaction_date >= start,
            InventoryTransaction.transaction_date <= end,
        )
        .group_by(InventoryTransaction.transaction_date, InventoryTransaction.transaction_type)
    )
    spend: dict[date, Decimal] = {}
    pnl: dict[date, Decimal] = {}
    for row in (await db.execute(stmt)).all():
        day, txn_type, line_total, gain = row
        if txn_type == TransactionType.BUY.value:
            spend[day] = Decimal(line_total)
        elif txn_type == TransactionType.SELL.value:
            pnl[day] = Decimal(gain)
    return spend, pnl


async def _realized_by_item(
    db: AsyncSession,
    user_id: int,
    date_from: date | None,
    date_to: date | None,
) -> list[DashboardItemGain]:
    card_stmt = (
        select(
            literal("card").label("item_type"),
            StockTransaction.card_id.label("card_id"),
            cast(null(), Integer).label("product_id"),
            Card.name.label("name"),
            Card.card_number.label("code"),
            Card.image_url.label("image_url"),
            func.coalesce(func.sum(StockTransaction.quantity), 0).label("quantity_sold"),
            func.coalesce(func.sum(StockTransaction.line_total), 0).label("proceeds"),
            func.coalesce(func.sum(StockTransaction.realized_gain), 0).label("realized_gain"),
        )
        .join(InventoryTransaction, InventoryTransaction.id == StockTransaction.transaction_id)
        .join(Card, Card.id == StockTransaction.card_id)
        .where(
            InventoryTransaction.user_id == user_id,
            InventoryTransaction.transaction_type == TransactionType.SELL.value,
            StockTransaction.card_id.is_not(None),
        )
        .group_by(StockTransaction.card_id, Card.name, Card.card_number, Card.image_url)
    )
    product_stmt = (
        select(
            literal("product").label("item_type"),
            cast(null(), Integer).label("card_id"),
            StockTransaction.product_id.label("product_id"),
            Product.name.label("name"),
            Product.category.label("code"),
            Product.image_url.label("image_url"),
            func.coalesce(func.sum(StockTransaction.quantity), 0).label("quantity_sold"),
            func.coalesce(func.sum(StockTransaction.line_total), 0).label("proceeds"),
            func.coalesce(func.sum(StockTransaction.realized_gain), 0).label("realized_gain"),
        )
        .join(InventoryTransaction, InventoryTransaction.id == StockTransaction.transaction_id)
        .join(Product, Product.id == StockTransaction.product_id)
        .where(
            InventoryTransaction.user_id == user_id,
            InventoryTransaction.transaction_type == TransactionType.SELL.value,
            StockTransaction.product_id.is_not(None),
        )
        .group_by(StockTransaction.product_id, Product.name, Product.category, Product.image_url)
    )
    card_stmt = _apply_date_filters(card_stmt, date_from, date_to)
    product_stmt = _apply_date_filters(product_stmt, date_from, date_to)
    combined = union_all(card_stmt, product_stmt).subquery()
    rows = (
        await db.execute(
            select(combined).order_by(combined.c.realized_gain.desc(), combined.c.name.asc())
        )
    ).all()
    return [
        DashboardItemGain(
            item_type=ItemType(row.item_type),
            card_id=row.card_id,
            product_id=row.product_id,
            name=row.name,
            code=row.code,
            image_url=row.image_url,
            quantity_sold=int(row.quantity_sold),
            proceeds=float(Decimal(row.proceeds).quantize(TWOPLACES)),
            realized_gain=float(Decimal(row.realized_gain).quantize(TWOPLACES)),
        )
        for row in rows
    ]


async def _top_holdings(db: AsyncSession, user_id: int, limit: int) -> list[DashboardHoldingRank]:
    card_stmt = (
        select(
            literal("card").label("item_type"),
            UserCardStock.card_id.label("card_id"),
            cast(null(), Integer).label("product_id"),
            Card.name.label("name"),
            Card.card_number.label("code"),
            Card.image_url.label("image_url"),
            UserCardStock.quantity,
            UserCardStock.avg_unit_cost,
            (UserCardStock.quantity * UserCardStock.avg_unit_cost).label("remaining_cost"),
        )
        .join(Card, Card.id == UserCardStock.card_id)
        .where(UserCardStock.user_id == user_id, UserCardStock.quantity > 0)
    )
    product_stmt = (
        select(
            literal("product").label("item_type"),
            cast(null(), Integer).label("card_id"),
            UserProductStock.product_id.label("product_id"),
            Product.name.label("name"),
            Product.category.label("code"),
            Product.image_url.label("image_url"),
            UserProductStock.quantity,
            UserProductStock.avg_unit_cost,
            (UserProductStock.quantity * UserProductStock.avg_unit_cost).label("remaining_cost"),
        )
        .join(Product, Product.id == UserProductStock.product_id)
        .where(UserProductStock.user_id == user_id, UserProductStock.quantity > 0)
    )
    combined = union_all(card_stmt, product_stmt).subquery()
    rows = (
        await db.execute(
            select(combined)
            .order_by(combined.c.remaining_cost.desc(), combined.c.name.asc())
            .limit(limit)
        )
    ).all()
    return [
        DashboardHoldingRank(
            item_type=ItemType(row.item_type),
            card_id=row.card_id,
            product_id=row.product_id,
            name=row.name,
            code=row.code,
            image_url=row.image_url,
            quantity=int(row.quantity),
            avg_unit_cost=float(row.avg_unit_cost),
            remaining_cost=float(Decimal(row.remaining_cost).quantize(TWOPLACES)),
        )
        for row in rows
    ]
