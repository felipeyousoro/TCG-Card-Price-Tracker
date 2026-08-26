"""drop set_code and card_image_id; add tcgplayer_id

Revision ID: a8e15f3c6d54
Revises: f6c93e1a4b32
Create Date: 2026-08-26 16:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a8e15f3c6d54"
down_revision: Union[str, None] = "f6c93e1a4b32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_card_game_name_set_code", "card", type_="unique")
    op.drop_column("card", "set_code")
    op.add_column(
        "card",
        sa.Column("tcgplayer_id", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_unique_constraint("uq_card_tcgplayer_id", "card", ["tcgplayer_id"])
    op.create_unique_constraint(
        "uq_card_game_name_set_name",
        "card",
        ["game", "name", "set_name"],
    )
    op.alter_column("card", "tcgplayer_id", server_default=None)
    op.drop_column("optcg_card", "card_image_id")
    op.add_column(
        "sync_job",
        sa.Column(
            "params",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("sync_job", "params")
    op.add_column("optcg_card", sa.Column("card_image_id", sa.String(), nullable=True))
    op.drop_constraint("uq_card_game_name_set_name", "card", type_="unique")
    op.drop_constraint("uq_card_tcgplayer_id", "card", type_="unique")
    op.drop_column("card", "tcgplayer_id")
    op.add_column("card", sa.Column("set_code", sa.String(), nullable=False, server_default=""))
    op.alter_column("card", "set_code", server_default=None)
    op.create_unique_constraint(
        "uq_card_game_name_set_code",
        "card",
        ["game", "name", "set_code"],
    )
