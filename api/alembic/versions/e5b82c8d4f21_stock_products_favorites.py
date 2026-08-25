"""split shared card identity from optcg_card detail

Revision ID: e5b82c8d4f21
Revises: d4a91b7c3e10
Create Date: 2026-08-25 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e5b82c8d4f21"
down_revision: Union[str, None] = "d4a91b7c3e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

XOR_CARD_PRODUCT = (
    "(card_id IS NOT NULL AND product_id IS NULL) OR (card_id IS NULL AND product_id IS NOT NULL)"
)


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("set_name", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_category", "product", ["category"], unique=False)
    op.create_index("ix_product_created_by_user_id", "product", ["created_by_user_id"], unique=False)

    op.create_table(
        "transaction",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=20), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transaction_user_id", "transaction", ["user_id"], unique=False)
    op.create_index("ix_transaction_transaction_type", "transaction", ["transaction_type"], unique=False)
    op.create_index("ix_transaction_transaction_date", "transaction", ["transaction_date"], unique=False)

    op.create_table(
        "stock_transaction",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(XOR_CARD_PRODUCT, name="ck_stock_transaction_card_xor_product"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transaction.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["card_id"], ["card.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stock_transaction_transaction_id", "stock_transaction", ["transaction_id"], unique=False)
    op.create_index("ix_stock_transaction_user_id", "stock_transaction", ["user_id"], unique=False)
    op.create_index("ix_stock_transaction_card_id", "stock_transaction", ["card_id"], unique=False)
    op.create_index("ix_stock_transaction_product_id", "stock_transaction", ["product_id"], unique=False)

    op.create_table(
        "user_card_stock",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("avg_unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["card_id"], ["card.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "card_id", name="uq_user_card_stock_user_card"),
    )
    op.create_index("ix_user_card_stock_user_id", "user_card_stock", ["user_id"], unique=False)
    op.create_index("ix_user_card_stock_card_id", "user_card_stock", ["card_id"], unique=False)

    op.create_table(
        "user_product_stock",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("avg_unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_user_product_stock_user_product"),
    )
    op.create_index("ix_user_product_stock_user_id", "user_product_stock", ["user_id"], unique=False)
    op.create_index("ix_user_product_stock_product_id", "user_product_stock", ["product_id"], unique=False)

    op.create_table(
        "favorite",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(XOR_CARD_PRODUCT, name="ck_favorite_card_xor_product"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["card_id"], ["card.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_favorite_user_id", "favorite", ["user_id"], unique=False)
    op.create_index("ix_favorite_card_id", "favorite", ["card_id"], unique=False)
    op.create_index("ix_favorite_product_id", "favorite", ["product_id"], unique=False)
    op.create_index(
        "uq_favorite_user_card",
        "favorite",
        ["user_id", "card_id"],
        unique=True,
        postgresql_where=sa.text("card_id IS NOT NULL"),
    )
    op.create_index(
        "uq_favorite_user_product",
        "favorite",
        ["user_id", "product_id"],
        unique=True,
        postgresql_where=sa.text("product_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_favorite_user_product", table_name="favorite")
    op.drop_index("uq_favorite_user_card", table_name="favorite")
    op.drop_index("ix_favorite_product_id", table_name="favorite")
    op.drop_index("ix_favorite_card_id", table_name="favorite")
    op.drop_index("ix_favorite_user_id", table_name="favorite")
    op.drop_table("favorite")

    op.drop_index("ix_user_product_stock_product_id", table_name="user_product_stock")
    op.drop_index("ix_user_product_stock_user_id", table_name="user_product_stock")
    op.drop_table("user_product_stock")

    op.drop_index("ix_user_card_stock_card_id", table_name="user_card_stock")
    op.drop_index("ix_user_card_stock_user_id", table_name="user_card_stock")
    op.drop_table("user_card_stock")

    op.drop_index("ix_stock_transaction_product_id", table_name="stock_transaction")
    op.drop_index("ix_stock_transaction_card_id", table_name="stock_transaction")
    op.drop_index("ix_stock_transaction_user_id", table_name="stock_transaction")
    op.drop_index("ix_stock_transaction_transaction_id", table_name="stock_transaction")
    op.drop_table("stock_transaction")

    op.drop_index("ix_transaction_transaction_date", table_name="transaction")
    op.drop_index("ix_transaction_transaction_type", table_name="transaction")
    op.drop_index("ix_transaction_user_id", table_name="transaction")
    op.drop_table("transaction")

    op.drop_index("ix_product_created_by_user_id", table_name="product")
    op.drop_index("ix_product_category", table_name="product")
    op.drop_table("product")
