from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import ItemType, TransactionType


class BuyLineIn(BaseModel):
    """One card or product line on a buy."""

    model_config = ConfigDict(extra="forbid")

    card_id: int | None = None
    product_id: int | None = None
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)

    @model_validator(mode="after")
    def exactly_one_item(self) -> "BuyLineIn":
        if (self.card_id is None) == (self.product_id is None):
            raise ValueError("Exactly one of card_id or product_id must be set")
        return self


class BuyCardRequest(BaseModel):
    """Single-line buy of a catalog card."""

    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    transaction_date: date
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0)


class BuyProductRequest(BaseModel):
    """Single-line buy of a catalog product."""

    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    transaction_date: date
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0)


class TransactionCreate(BaseModel):
    """Multi-line buy order."""

    model_config = ConfigDict(extra="forbid")

    transaction_date: date
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0)
    lines: list[BuyLineIn] = Field(min_length=1)


class BuyImportRequest(BaseModel):
    """Paste import: one payload is one order of catalog cards."""

    model_config = ConfigDict(extra="forbid")

    transaction_date: date
    shipping_cost: Decimal = Field(default=Decimal("0"), ge=0)
    text: str = Field(min_length=1)


class ImportLineError(BaseModel):
    line: int
    message: str


class BuyImportResult(BaseModel):
    fetched: int
    inserted: int
    skipped: int
    errors: list[ImportLineError] = Field(default_factory=list)
    transaction_id: UUID | None = None


class StockLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    card_id: int | None
    product_id: int | None
    name: str
    quantity: int
    unit_price: float
    shipping_per_unit: float
    effective_unit_cost: float
    line_total: float


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_type: TransactionType
    transaction_date: date
    shipping_cost: float
    created_at: datetime
    lines: list[StockLineRead]
    total: float


class HoldingItem(BaseModel):
    item_type: ItemType
    card_id: int | None = None
    product_id: int | None = None
    name: str
    code: str | None = None
    image_url: str | None = None
    quantity: int
    avg_unit_cost: float


class StockQuantities(BaseModel):
    cards: dict[str, int]
    products: dict[str, int]
