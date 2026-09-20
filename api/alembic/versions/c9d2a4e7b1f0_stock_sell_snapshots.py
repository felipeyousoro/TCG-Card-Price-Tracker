"""add sell snapshot cost and realized gain

Revision ID: c9d2a4e7b1f0
Revises: f6c93e1a4b32
Create Date: 2026-09-20 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d2a4e7b1f0"
down_revision: Union[str, None] = "f6c93e1a4b32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "stock_transaction",
        sa.Column("avg_unit_cost_at_sale", sa.Numeric(12, 2), nullable=True),
    )
    op.add_column(
        "stock_transaction",
        sa.Column("realized_gain", sa.Numeric(12, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("stock_transaction", "realized_gain")
    op.drop_column("stock_transaction", "avg_unit_cost_at_sale")
