from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy import Integer, cast, func, literal, null, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.auth.http_exceptions import BadRequestException, NotFoundException
from ..cards.models import Card
from ..products.enums import ProductCategory
from ..products.models import Product
from ..products.schemas import ProductCreate
from ..products.service import ProductCatalogService
from .enums import ItemType, TransactionType
from .models import InventoryTransaction, StockTransaction, UserCardStock, UserProductStock
from .schemas import (
    BuyCardRequest,
    BuyImportRequest,
    BuyImportResult,
    BuyLineIn,
    BuyProductRequest,
    HoldingItem,
    ImportLineError,
    StockLineRead,
    StockQuantities,
    TransactionCreate,
    TransactionRead,
)

TWOPLACES = Decimal("0.01")


class StockService:
    """Record buys, maintain aggregate holdings, and list history."""

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
            notes=payload.transaction_notes,
            lines=[
                BuyLineIn(
                    card_id=card_id,
                    quantity=payload.quantity,
                    unit_price=payload.unit_price,
                    notes=payload.notes,
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
            notes=payload.transaction_notes,
            lines=[
                BuyLineIn(
                    product_id=product_id,
                    quantity=payload.quantity,
                    unit_price=payload.unit_price,
                    notes=payload.notes,
                )
            ],
        )

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
            notes=payload.notes,
            lines=payload.lines,
        )

    async def record_buy(
        self,
        db: AsyncSession,
        user_id: int,
        transaction_date,
        lines: list[BuyLineIn],
        notes: str | None = None,
    ) -> TransactionRead:
        if not lines:
            raise BadRequestException(detail="At least one line is required")

        header = InventoryTransaction(
            user_id=user_id,
            transaction_type=TransactionType.BUY.value,
            transaction_date=transaction_date,
            notes=notes,
        )
        db.add(header)
        await db.flush()

        for line in lines:
            qty = int(line.quantity)
            unit_price = Decimal(line.unit_price).quantize(TWOPLACES)
            stock_line = StockTransaction(
                transaction_id=header.id,
                user_id=user_id,
                card_id=line.card_id,
                product_id=line.product_id,
                quantity=qty,
                unit_price=unit_price,
                line_total=(Decimal(qty) * unit_price).quantize(TWOPLACES),
                notes=line.notes,
            )
            db.add(stock_line)
            if line.card_id is not None:
                await _apply_card_buy(db, user_id, line.card_id, qty, unit_price)
            else:
                await _apply_product_buy(db, user_id, line.product_id, qty, unit_price)  # type: ignore[arg-type]

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
                await _reverse_card_buy(db, user_id, line.card_id, line.quantity, line.unit_price)
            elif line.product_id is not None:
                await _reverse_product_buy(db, user_id, line.product_id, line.quantity, line.unit_price)

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

    async def import_buys_from_text(
        self,
        db: AsyncSession,
        user_id: int,
        payload: BuyImportRequest,
    ) -> BuyImportResult:
        parsed, errors = await self._parse_import_lines(db, user_id, payload.text)
        fetched = parsed.fetched
        skipped = len(errors)
        if not parsed.lines:
            return BuyImportResult(
                fetched=fetched,
                inserted=0,
                skipped=skipped,
                errors=errors,
                transaction_id=None,
            )

        result = await self.record_buy(
            db,
            user_id=user_id,
            transaction_date=payload.transaction_date,
            notes=payload.notes,
            lines=parsed.lines,
        )
        return BuyImportResult(
            fetched=fetched,
            inserted=len(parsed.lines),
            skipped=skipped,
            errors=errors,
            transaction_id=result.id,
        )

    async def _parse_import_lines(
        self,
        db: AsyncSession,
        user_id: int,
        text: str,
    ) -> tuple["_ParsedImport", list[ImportLineError]]:
        lines: list[BuyLineIn] = []
        errors: list[ImportLineError] = []
        fetched = 0

        for index, raw in enumerate(text.splitlines(), start=1):
            row = raw.strip()
            if not row:
                continue
            parts = [part.strip() for part in row.split(";")]
            if len(parts) >= 2 and parts[0].lower() == "card_set_id" and parts[1].lower() == "product_name":
                continue
            fetched += 1
            if len(parts) < 4:
                errors.append(
                    ImportLineError(
                        line=index,
                        message="Expected card_set_id;product_name;quantity;unit_price;notes",
                    )
                )
                continue

            card_set_id, product_name, qty_raw, price_raw = parts[0], parts[1], parts[2], parts[3]
            notes = ";".join(parts[4:]).strip() or None if len(parts) > 4 else None

            if bool(card_set_id) == bool(product_name):
                errors.append(
                    ImportLineError(
                        line=index,
                        message="Set exactly one of card_set_id or product_name",
                    )
                )
                continue

            try:
                quantity = int(qty_raw)
                if quantity < 1:
                    raise ValueError
            except ValueError:
                errors.append(ImportLineError(line=index, message="Quantity must be a positive integer"))
                continue

            try:
                unit_price = Decimal(price_raw)
                if unit_price < 0:
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                errors.append(ImportLineError(line=index, message="Unit price must be a non-negative number"))
                continue

            if card_set_id:
                matches = list(
                    (await db.execute(select(Card).where(Card.card_number == card_set_id))).scalars().all()
                )
                if len(matches) != 1:
                    errors.append(
                        ImportLineError(
                            line=index,
                            message=(
                                f"No card matches card_set_id {card_set_id!r}"
                                if not matches
                                else f"Multiple cards match card_set_id {card_set_id!r}"
                            ),
                        )
                    )
                    continue
                lines.append(
                    BuyLineIn(
                        card_id=matches[0].id,
                        quantity=quantity,
                        unit_price=unit_price,
                        notes=notes,
                    )
                )
                continue

            matches = await self.products.find_by_name_ilike(db, product_name)
            if len(matches) > 1:
                errors.append(
                    ImportLineError(
                        line=index,
                        message=f"Multiple products match {product_name!r}",
                    )
                )
                continue
            if len(matches) == 1:
                product = matches[0]
            else:
                created = await self.products.create(
                    db,
                    ProductCreate(name=product_name, category=ProductCategory.OTHER),
                    user_id,
                    commit=False,
                )
                product_id = created.id
                lines.append(
                    BuyLineIn(
                        product_id=product_id,
                        quantity=quantity,
                        unit_price=unit_price,
                        notes=notes,
                    )
                )
                continue

            lines.append(
                BuyLineIn(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    notes=notes,
                )
            )

        return _ParsedImport(fetched=fetched, lines=lines), errors


class _ParsedImport:
    def __init__(self, fetched: int, lines: list[BuyLineIn]) -> None:
        self.fetched = fetched
        self.lines = lines


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
                line_total=float(line.line_total),
                notes=line.notes,
            )
        )
        total += Decimal(line.line_total)
    return TransactionRead(
        id=header.id,
        transaction_type=TransactionType(header.transaction_type),
        transaction_date=header.transaction_date,
        notes=header.notes,
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
