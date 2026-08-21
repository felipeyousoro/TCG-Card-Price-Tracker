"""add unique constraint on optcg_card card_name and set_id

Revision ID: a4f8c2e91b07
Revises: 1c27d01dc450
Create Date: 2026-08-21 16:40:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "a4f8c2e91b07"
down_revision: Union[str, None] = "1c27d01dc450"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_optcg_card_name_set_id",
        "optcg_card",
        ["card_name", "set_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_optcg_card_name_set_id", "optcg_card", type_="unique")
