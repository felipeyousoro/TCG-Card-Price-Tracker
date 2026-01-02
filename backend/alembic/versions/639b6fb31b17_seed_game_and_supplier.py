"""seed_game_and_supplier

Revision ID: 639b6fb31b17
Revises: 0a374f29bfad
Create Date: 2026-01-02 19:56:08.377731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '639b6fb31b17'
down_revision: Union[str, None] = '0a374f29bfad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("INSERT INTO game (name) VALUES ('one piece')")
    )
    op.execute(
        sa.text("INSERT INTO supplier (name) VALUES ('liga')")
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM supplier WHERE name = 'liga'")
    )
    op.execute(
        sa.text("DELETE FROM game WHERE name = 'one piece'")
    )
