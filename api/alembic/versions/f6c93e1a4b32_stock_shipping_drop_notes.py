"""add shipping cost fields and drop stock notes

Revision ID: f6c93e1a4b32
Revises: e5b82c8d4f21
Create Date: 2026-08-25 12:33:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6c93e1a4b32"
down_revision: Union[str, None] = "e5b82c8d4f21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transaction",
        sa.Column("shipping_cost", sa.Numeric(12, 2), server_default="0", nullable=False),
    )
    op.drop_column("transaction", "notes")

    op.add_column(
        "stock_transaction",
        sa.Column("shipping_per_unit", sa.Numeric(12, 4), server_default="0", nullable=False),
    )
    op.add_column(
        "stock_transaction",
        sa.Column("effective_unit_cost", sa.Numeric(12, 4), nullable=True),
    )
    op.execute("UPDATE stock_transaction SET effective_unit_cost = unit_price")
    op.alter_column("stock_transaction", "effective_unit_cost", nullable=False)
    op.drop_column("stock_transaction", "notes")

    op.alter_column("transaction", "shipping_cost", server_default=None)
    op.alter_column("stock_transaction", "shipping_per_unit", server_default=None)


def downgrade() -> None:
    op.add_column("stock_transaction", sa.Column("notes", sa.Text(), nullable=True))
    op.drop_column("stock_transaction", "effective_unit_cost")
    op.drop_column("stock_transaction", "shipping_per_unit")

    op.add_column("transaction", sa.Column("notes", sa.Text(), nullable=True))
    op.drop_column("transaction", "shipping_cost")
