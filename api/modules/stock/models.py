import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database.models import TimestampMixin
from ...core.database.session import Base


XOR_CARD_PRODUCT = (
    "(card_id IS NOT NULL AND product_id IS NULL) OR (card_id IS NULL AND product_id IS NOT NULL)"
)


class InventoryTransaction(Base, TimestampMixin):
    """One buy or sell event (a store visit or online order)."""

    __tablename__ = "transaction"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        init=False,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(20), index=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    lines: Mapped[list["StockTransaction"]] = relationship(
        back_populates="transaction",
        cascade="all, delete-orphan",
        init=False,
        default_factory=list,
    )


class StockTransaction(Base):
    """One card or product line inside a transaction."""

    __tablename__ = "stock_transaction"
    __table_args__ = (
        CheckConstraint(XOR_CARD_PRODUCT, name="ck_stock_transaction_card_xor_product"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        init=False,
    )
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transaction.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    card_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("card.id"),
        default=None,
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        default=None,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    transaction: Mapped[InventoryTransaction] = relationship(back_populates="lines", init=False)


class UserCardStock(Base, TimestampMixin):
    """Aggregate holding of one catalog card for one user."""

    __tablename__ = "user_card_stock"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card_stock_user_card"),)

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        nullable=False,
        primary_key=True,
        init=False,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("card.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    avg_unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class UserProductStock(Base, TimestampMixin):
    """Aggregate holding of one catalog product for one user."""

    __tablename__ = "user_product_stock"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_stock_user_product"),
    )

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        nullable=False,
        primary_key=True,
        init=False,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    avg_unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))
