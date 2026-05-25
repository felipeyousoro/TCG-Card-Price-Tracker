"""seed default game and supplier

Revision ID: ab8fba5d753b
Revises: 4e582581ee30
Create Date: 2026-05-24 23:34:18.564828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab8fba5d753b'
down_revision: Union[str, None] = '4e582581ee30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    game_table = sa.table(
        "game",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    supplier_table = sa.table(
        "supplier",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )

    op.bulk_insert(game_table, [{"id": 1, "name": "One Piece"}])
    op.bulk_insert(supplier_table, [{"id": 1, "name": "Liga"}])


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM supplier WHERE id = 1"))
    op.execute(sa.text("DELETE FROM game WHERE id = 1"))
