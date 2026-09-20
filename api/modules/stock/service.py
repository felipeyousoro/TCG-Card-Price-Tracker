from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy import Integer, cast, func, literal, null, or_, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.auth.http_exceptions import BadRequestException, NotFoundException
from ..cards.models import Card
from ..products.models import Product
from ..products.service import ProductCatalogService
from .enums import ItemType, TransactionType
from .models import InventoryTransaction, StockTransaction, UserCardStock, UserProductStock
from .schemas import (
    BuyCardRequest,
    BuyLineIn,
    BuyProductRequest,
    HoldingItem,
    ImportPreviewLine,
    ImportPreviewMatch,
    ImportPreviewResult,
    SellRequest,
    StockLineRead,
    StockQuantities,
    TransactionCreate,
    TransactionRead,
)

TWOPLACES = Decimal("0.01")
FOURPLACES = Decimal("0.0001")


class StockService:
    """Record buys and sells, maintain aggregate holdings, and list history."""

    def __init__(self, products: ProductCatalogService | None = None) -> None:
        self.products = products or ProductCatalogService()

    async def buy_card(
        self,
        db: AsyncSession,
        user_id: int,
        card_id: int,
        payload: BuyCardRequest,
    ) -> TransactionRead:
        await _require_card(db, card_id)
        return await self.record_buy(
            db,
            user_id=user_id,
            transaction_date=payload.transaction_date,
            shipping_cost=payload.shipping_cost,
            lines=[
                BuyLineIn(
                    card_id=card_id,
                    quantity=payload.quantity,
                    unit_price=payload.unit_price,
                )
            ],
        )

    async def buy_product(
        self,
        db: AsyncSession,
        user_id: int,
        product_id: int,
        payload: BuyProductRequest,
    ) -> TransactionRead:
        await _require_product(db, product_id)
        return await self.record_buy(
            db,
            user_id=user_id,
            transaction_date=payload.transaction_date,
            shipping_cost=payload.shipping_cost,
            lines=[
                BuyLineIn(
                    product_id=product_id,
                    quantity=payload.quantity,
                    unit_price=payload.unit_price,
                )
            ],
        )

    async def sell_card(
        self,
        db: AsyncSession,
        user_id: int,
        card_id: int,
        payload: SellRequest,
    ) -> TransactionRead:
        await _require_card(db, card_id)
        return await self.record_sell(
            db,
            user_id=user_id,
            transaction_date=payload.transaction_date,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            card_id=card_id,
        )

    async def sell_product(
        self,
        db: AsyncSession,
        user_id: int,
        product_id: int,
        payload: SellRequest,
    ) -> TransactionRead:
        await _require_product(db, product_id)
        return await self.record_sell(
            db,
            user_id=user_id,
            transaction_date=payload.transaction_date,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            product_id=product_id,
        )

    async def record_sell(
        self,
        db: AsyncSession,
        user_id: int,
        transaction_date,
        quantity: int,
        unit_price: Decimal,
        card_id: int | None = None,
        product_id: int | None = None,
    ) -> TransactionRead:
        if (card_id is None) == (product_id is None):
            raise BadRequestException(detail="Exactly one of card_id or product_id must be set")

        qty = int(quantity)
        unit_price = Decimal(unit_price).quantize(TWOPLACES)
        holding = await _load_holding(db, user_id, card_id=card_id, product_id=product_id)
        if holding is None or int(holding.quantity) < qty:
            raise BadRequestException(detail="Not enough quantity to sell")

        avg_at_sale = Decimal(holding.avg_unit_cost).quantize(TWOPLACES)
        realized_gain = ((unit_price - avg_at_sale) * Decimal(qty)).quantize(TWOPLACES)
        line_total = (unit_price * Decimal(qty)).quantize(TWOPLACES)

        header = InventoryTransaction(
            user_id=user_id,
            transaction_type=TransactionType.SELL.value,
            transaction_date=transaction_date,
            shipping_cost=Decimal("0.00"),
        )
        db.add(header)
        await db.flush()

        db.add(
            StockTransaction(
                transaction_id=header.id,
                user_id=user_id,
                card_id=card_id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                shipping_per_unit=Decimal("0"),
                effective_unit_cost=unit_price.quantize(FOURPLACES),
                line_total=line_total,
                avg_unit_cost_at_sale=avg_at_sale,
                realized_gain=realized_gain,
            )
        )
        await _apply_sell_holding(db, holding, qty)
        await db.commit()
        return await self.get_transaction(db, user_id, header.id)

    async def create_transaction(
        self,
        db: AsyncSession,
        user_id: int,
        payload: TransactionCreate,
    ) -> TransactionRead:
        for line in payload.lines:
            if line.card_id is not None:
                await _require_card(db, line.card_id)
            else:
                await _require_product(db, line.product_id)  # type: ignore[arg-type]
        return await self.record_buy(
            db,
            user_id=user_id,
            transaction_date=payload.transaction_date,
            shipping_cost=payload.shipping_cost,
            lines=payload.lines,
        )

    async def record_buy(
        self,
        db: AsyncSession,
        user_id: int,
        transaction_date,
        lines: list[BuyLineIn],
        shipping_cost: Decimal = Decimal("0"),
    ) -> TransactionRead:
        if not lines:
            raise BadRequestException(detail="At least one line is required")

        shipping_cost = Decimal(shipping_cost).quantize(TWOPLACES)
        total_qty = sum(int(line.quantity) for line in lines)
        shipping_per_unit = (
            (shipping_cost / Decimal(total_qty)).quantize(FOURPLACES) if total_qty else Decimal("0")
        )

        header = InventoryTransaction(
            user_id=user_id,
            transaction_type=TransactionType.BUY.value,
            transaction_date=transaction_date,
            shipping_cost=shipping_cost,
        )
        db.add(header)
        await db.flush()

        prepared: list[tuple[BuyLineIn, int, Decimal, Decimal, Decimal]] = []
        merchandise = Decimal("0")
        for line in lines:
            qty = int(line.quantity)
            unit_price = Decimal(line.unit_price).quantize(TWOPLACES)
            effective = (unit_price + shipping_per_unit).quantize(FOURPLACES)
            line_total = (effective * Decimal(qty)).quantize(TWOPLACES)
            merchandise += unit_price * Decimal(qty)
            prepared.append((line, qty, unit_price, effective, line_total))

        expected = (merchandise + shipping_cost).quantize(TWOPLACES)
        actual = sum(item[4] for item in prepared)
        leftover = expected - actual
        if leftover and prepared:
            last_line, last_qty, last_unit, last_effective, last_total = prepared[-1]
            prepared[-1] = (
                last_line,
                last_qty,
                last_unit,
                last_effective,
                (last_total + leftover).quantize(TWOPLACES),
            )

        for line, qty, unit_price, effective, line_total in prepared:
            stock_line = StockTransaction(
                transaction_id=header.id,
                user_id=user_id,
                card_id=line.card_id,
                product_id=line.product_id,
                quantity=qty,
                unit_price=unit_price,
                shipping_per_unit=shipping_per_unit,
                effective_unit_cost=effective,
                line_total=line_total,
            )
            db.add(stock_line)
            if line.card_id is not None:
                await _apply_card_buy(db, user_id, line.card_id, qty, effective)
            else:
                await _apply_product_buy(db, user_id, line.product_id, qty, effective)  # type: ignore[arg-type]

        await db.commit()
        return await self.get_transaction(db, user_id, header.id)

    async def get_transaction(
        self,
        db: AsyncSession,
        user_id: int,
        transaction_id: UUID,
    ) -> TransactionRead:
        header = await _load_transaction(db, user_id, transaction_id)
        if header is None:
            raise NotFoundException(detail="Transaction not found")
        return await _to_transaction_read(db, header)

    async def list_transactions(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int,
        limit: int,
    ) -> dict:
        count_stmt = select(func.count()).select_from(InventoryTransaction).where(
            InventoryTransaction.user_id == user_id
        )
        total = int((await db.execute(count_stmt)).scalar_one())
        stmt = (
            select(InventoryTransaction)
            .where(InventoryTransaction.user_id == user_id)
            .options(selectinload(InventoryTransaction.lines))
            .order_by(
                InventoryTransaction.transaction_date.desc(),
                InventoryTransaction.created_at.desc(),
            )
            .offset(skip)
            .limit(limit)
        )
        headers = list((await db.execute(stmt)).scalars().unique().all())
        data = [await _to_transaction_read(db, header) for header in headers]
        return {"data": [item.model_dump(mode="json") for item in data], "total_count": total}

    async def delete_transaction(self, db: AsyncSession, user_id: int, transaction_id: UUID) -> None:
        header = await _load_transaction(db, user_id, transaction_id)
        if header is None:
            raise NotFoundException(detail="Transaction not found")
        if header.transaction_type != TransactionType.BUY.value:
            raise BadRequestException(detail="Only buy transactions can be deleted")

        for line in header.lines:
            if line.card_id is not None:
                await _reverse_card_buy(
                    db, user_id, line.card_id, line.quantity, line.effective_unit_cost
                )
            elif line.product_id is not None:
                await _reverse_product_buy(
                    db, user_id, line.product_id, line.quantity, line.effective_unit_cost
                )

        await db.delete(header)
        await db.commit()

    async def list_holdings(self, db: AsyncSession, user_id: int, skip: int, limit: int) -> dict:
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
            )
            .join(Product, Product.id == UserProductStock.product_id)
            .where(UserProductStock.user_id == user_id, UserProductStock.quantity > 0)
        )
        combined = union_all(card_stmt, product_stmt).subquery()
        total = int(
            (await db.execute(select(func.count()).select_from(combined))).scalar_one()
        )
        rows = (
            await db.execute(
                select(combined).order_by(combined.c.name.asc()).offset(skip).limit(limit)
            )
        ).all()
        data = [
            HoldingItem(
                item_type=ItemType(row.item_type),
                card_id=row.card_id,
                product_id=row.product_id,
                name=row.name,
                code=row.code,
                image_url=row.image_url,
                quantity=int(row.quantity),
                avg_unit_cost=float(row.avg_unit_cost),
            )
            for row in rows
        ]
        return {"data": [item.model_dump(mode="json") for item in data], "total_count": total}

    async def list_quantities(self, db: AsyncSession, user_id: int) -> StockQuantities:
        card_rows = (
            await db.execute(
                select(UserCardStock.card_id, UserCardStock.quantity).where(
                    UserCardStock.user_id == user_id,
                    UserCardStock.quantity > 0,
                )
            )
        ).all()
        product_rows = (
            await db.execute(
                select(UserProductStock.product_id, UserProductStock.quantity).where(
                    UserProductStock.user_id == user_id,
                    UserProductStock.quantity > 0,
                )
            )
        ).all()
        return StockQuantities(
            cards={str(row.card_id): int(row.quantity) for row in card_rows},
            products={str(row.product_id): int(row.quantity) for row in product_rows},
        )

    async def preview_import(self, db: AsyncSession, text: str) -> ImportPreviewResult:
        return await _parse_import_preview(db, text)


def _ilike_contains(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


async def _parse_import_preview(db: AsyncSession, text: str) -> ImportPreviewResult:
    lines: list[ImportPreviewLine] = []
    unmatched: list[str] = []

    for raw in text.splitlines():
        row = raw.strip()
        if not row:
            continue
        parts = [part.strip() for part in row.split(";")]
        if len(parts) >= 2 and parts[0].lower() == "card_set_id" and parts[1].lower() == "variant":
            continue

        if len(parts) < 4:
            unmatched.append(raw)
            continue

        card_set_id, variant, qty_raw, price_raw = parts[0], parts[1], parts[2], parts[3]
        if not card_set_id:
            unmatched.append(raw)
            continue

        try:
            quantity = int(qty_raw)
            if quantity < 1:
                raise ValueError
        except ValueError:
            unmatched.append(raw)
            continue

        try:
            unit_price = Decimal(price_raw)
            if unit_price < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            unmatched.append(raw)
            continue

        stmt = (
            select(Card)
            .where(func.lower(Card.card_number) == card_set_id.lower())
            .order_by(Card.id.asc())
        )
        if variant:
            pattern = _ilike_contains(variant)
            stmt = stmt.where(
                or_(
                    Card.name.ilike(pattern, escape="\\"),
                    Card.rarity.ilike(pattern, escape="\\"),
                )
            )
        matches = list((await db.execute(stmt)).scalars().all())
        if not matches:
            unmatched.append(raw)
            continue

        preview_matches = [
            ImportPreviewMatch(
                card_id=card.id,
                name=card.name,
                card_number=card.card_number,
                rarity=card.rarity,
                image_url=card.image_url,
            )
            for card in matches
        ]
        lines.append(
            ImportPreviewLine(
                quantity=quantity,
                unit_price=float(unit_price),
                auto_chosen=len(matches) > 1,
                selected_card_id=preview_matches[0].card_id,
                matches=preview_matches,
            )
        )

    return ImportPreviewResult(lines=lines, unmatched_text="\n".join(unmatched))


async def _require_card(db: AsyncSession, card_id: int) -> None:
    exists = (await db.execute(select(Card.id).where(Card.id == card_id))).scalar_one_or_none()
    if exists is None:
        raise NotFoundException(detail="Card not found")


async def _require_product(db: AsyncSession, product_id: int) -> None:
    exists = (await db.execute(select(Product.id).where(Product.id == product_id))).scalar_one_or_none()
    if exists is None:
        raise NotFoundException(detail="Product not found")


async def _load_transaction(
    db: AsyncSession,
    user_id: int,
    transaction_id: UUID,
) -> InventoryTransaction | None:
    stmt = (
        select(InventoryTransaction)
        .where(
            InventoryTransaction.id == transaction_id,
            InventoryTransaction.user_id == user_id,
        )
        .options(selectinload(InventoryTransaction.lines))
    )
    return (await db.execute(stmt)).scalars().unique().one_or_none()


async def _to_transaction_read(db: AsyncSession, header: InventoryTransaction) -> TransactionRead:
    names = await _line_names(db, header.lines)
    line_reads: list[StockLineRead] = []
    total = Decimal("0")
    for line in header.lines:
        key = ("card", line.card_id) if line.card_id is not None else ("product", line.product_id)
        line_reads.append(
            StockLineRead(
                id=line.id,
                card_id=line.card_id,
                product_id=line.product_id,
                name=names.get(key, "Unknown"),
                quantity=line.quantity,
                unit_price=float(line.unit_price),
                shipping_per_unit=float(line.shipping_per_unit),
                effective_unit_cost=float(line.effective_unit_cost),
                line_total=float(line.line_total),
                avg_unit_cost_at_sale=(
                    float(line.avg_unit_cost_at_sale) if line.avg_unit_cost_at_sale is not None else None
                ),
                realized_gain=float(line.realized_gain) if line.realized_gain is not None else None,
            )
        )
        total += Decimal(line.line_total)
    return TransactionRead(
        id=header.id,
        transaction_type=TransactionType(header.transaction_type),
        transaction_date=header.transaction_date,
        shipping_cost=float(header.shipping_cost),
        created_at=header.created_at,
        lines=line_reads,
        total=float(total),
    )


async def _line_names(
    db: AsyncSession,
    lines: list[StockTransaction],
) -> dict[tuple[str, int | None], str]:
    card_ids = [line.card_id for line in lines if line.card_id is not None]
    product_ids = [line.product_id for line in lines if line.product_id is not None]
    names: dict[tuple[str, int | None], str] = {}
    if card_ids:
        rows = (await db.execute(select(Card.id, Card.name).where(Card.id.in_(card_ids)))).all()
        names.update({("card", row.id): row.name for row in rows})
    if product_ids:
        rows = (await db.execute(select(Product.id, Product.name).where(Product.id.in_(product_ids)))).all()
        names.update({("product", row.id): row.name for row in rows})
    return names


async def _load_holding(
    db: AsyncSession,
    user_id: int,
    card_id: int | None,
    product_id: int | None,
) -> UserCardStock | UserProductStock | None:
    if card_id is not None:
        return (
            await db.execute(
                select(UserCardStock).where(
                    UserCardStock.user_id == user_id,
                    UserCardStock.card_id == card_id,
                )
            )
        ).scalar_one_or_none()
    return (
        await db.execute(
            select(UserProductStock).where(
                UserProductStock.user_id == user_id,
                UserProductStock.product_id == product_id,
            )
        )
    ).scalar_one_or_none()


async def _apply_sell_holding(
    db: AsyncSession,
    holding: UserCardStock | UserProductStock,
    quantity: int,
) -> None:
    new_qty = int(holding.quantity) - quantity
    if new_qty < 0:
        raise BadRequestException(detail="Not enough quantity to sell")
    if new_qty == 0:
        await db.delete(holding)
        return
    holding.quantity = new_qty
    holding.updated_at = datetime.now(UTC)


async def _apply_card_buy(
    db: AsyncSession,
    user_id: int,
    card_id: int,
    quantity: int,
    unit_price: Decimal,
) -> None:
    holding = (
        await db.execute(
            select(UserCardStock).where(UserCardStock.user_id == user_id, UserCardStock.card_id == card_id)
        )
    ).scalar_one_or_none()
    _upsert_holding(db, holding, UserCardStock, user_id, "card_id", card_id, quantity, unit_price)


async def _apply_product_buy(
    db: AsyncSession,
    user_id: int,
    product_id: int,
    quantity: int,
    unit_price: Decimal,
) -> None:
    holding = (
        await db.execute(
            select(UserProductStock).where(
                UserProductStock.user_id == user_id,
                UserProductStock.product_id == product_id,
            )
        )
    ).scalar_one_or_none()
    _upsert_holding(db, holding, UserProductStock, user_id, "product_id", product_id, quantity, unit_price)


def _upsert_holding(
    db: AsyncSession,
    holding: UserCardStock | UserProductStock | None,
    model: type,
    user_id: int,
    fk_name: str,
    fk_value: int,
    quantity: int,
    unit_price: Decimal,
) -> None:
    if holding is None:
        kwargs = {
            "user_id": user_id,
            fk_name: fk_value,
            "quantity": quantity,
            "avg_unit_cost": unit_price.quantize(TWOPLACES),
        }
        db.add(model(**kwargs))
        return

    old_qty = int(holding.quantity)
    old_avg = Decimal(holding.avg_unit_cost)
    new_qty = old_qty + quantity
    new_avg = ((old_qty * old_avg) + (quantity * unit_price)) / Decimal(new_qty)
    holding.quantity = new_qty
    holding.avg_unit_cost = new_avg.quantize(TWOPLACES)
    holding.updated_at = datetime.now(UTC)


async def _reverse_card_buy(
    db: AsyncSession,
    user_id: int,
    card_id: int,
    quantity: int,
    unit_price: Decimal,
) -> None:
    holding = (
        await db.execute(
            select(UserCardStock).where(UserCardStock.user_id == user_id, UserCardStock.card_id == card_id)
        )
    ).scalar_one_or_none()
    await _reverse_holding(db, holding, quantity, unit_price)


async def _reverse_product_buy(
    db: AsyncSession,
    user_id: int,
    product_id: int,
    quantity: int,
    unit_price: Decimal,
) -> None:
    holding = (
        await db.execute(
            select(UserProductStock).where(
                UserProductStock.user_id == user_id,
                UserProductStock.product_id == product_id,
            )
        )
    ).scalar_one_or_none()
    await _reverse_holding(db, holding, quantity, unit_price)


async def _reverse_holding(
    db: AsyncSession,
    holding: UserCardStock | UserProductStock | None,
    quantity: int,
    unit_price: Decimal,
) -> None:
    if holding is None:
        raise BadRequestException(detail="Cannot reverse a buy with no matching holding")
    new_qty = int(holding.quantity) - quantity
    if new_qty < 0:
        raise BadRequestException(detail="Reversing this buy would make holdings negative")
    if new_qty == 0:
        await db.delete(holding)
        return
    remaining_cost = (Decimal(holding.quantity) * Decimal(holding.avg_unit_cost)) - (
        Decimal(quantity) * Decimal(unit_price)
    )
    holding.quantity = new_qty
    holding.avg_unit_cost = (max(remaining_cost, Decimal("0")) / Decimal(new_qty)).quantize(TWOPLACES)
    holding.updated_at = datetime.now(UTC)
