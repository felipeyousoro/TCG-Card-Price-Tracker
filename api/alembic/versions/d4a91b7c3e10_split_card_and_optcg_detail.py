"""split shared card identity from optcg_card detail

Revision ID: d4a91b7c3e10
Revises: c8f5d02e3b29
Create Date: 2026-08-25 10:06:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4a91b7c3e10"
down_revision: Union[str, None] = "c8f5d02e3b29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "card",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("set_name", sa.String(), nullable=False),
        sa.Column("set_code", sa.String(), nullable=False),
        sa.Column("card_number", sa.String(), nullable=False),
        sa.Column("rarity", sa.String(), nullable=False),
        sa.Column("card_type", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "game",
            "name",
            "set_code",
            name="uq_card_game_name_set_code",
        ),
    )
    op.create_index("ix_card_game", "card", ["game"], unique=False)

    op.execute(
        sa.text(
            """
            INSERT INTO card (
                id, game, name, set_name, set_code, card_number,
                rarity, card_type, image_url, created_at, updated_at
            )
            SELECT
                id, 'optcg', card_name, set_name, set_id, card_set_id,
                rarity, card_type, card_image, created_at, updated_at
            FROM optcg_card
            """
        )
    )
    op.execute(
        sa.text(
            """
            SELECT setval(
                pg_get_serial_sequence('card', 'id'),
                COALESCE((SELECT MAX(id) FROM card), 1),
                (SELECT EXISTS (SELECT 1 FROM card))
            )
            """
        )
    )

    op.add_column("optcg_card", sa.Column("card_id", sa.Integer(), nullable=True))
    op.execute(sa.text("UPDATE optcg_card SET card_id = id"))
    op.alter_column("optcg_card", "card_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key(
        "fk_optcg_card_card_id",
        "optcg_card",
        "card",
        ["card_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("uq_optcg_card_name_set_id", "optcg_card", type_="unique")
    op.drop_column("optcg_card", "card_name")
    op.drop_column("optcg_card", "set_name")
    op.drop_column("optcg_card", "set_id")
    op.drop_column("optcg_card", "rarity")
    op.drop_column("optcg_card", "card_set_id")
    op.drop_column("optcg_card", "card_type")
    op.drop_column("optcg_card", "card_image")

    op.drop_constraint("optcg_card_pkey", "optcg_card", type_="primary")
    op.drop_column("optcg_card", "id")
    op.create_primary_key("optcg_card_pkey", "optcg_card", ["card_id"])


def downgrade() -> None:
    op.add_column("optcg_card", sa.Column("id", sa.Integer(), nullable=True))
    op.add_column("optcg_card", sa.Column("card_name", sa.String(), nullable=True))
    op.add_column("optcg_card", sa.Column("set_name", sa.String(), nullable=True))
    op.add_column("optcg_card", sa.Column("set_id", sa.String(), nullable=True))
    op.add_column("optcg_card", sa.Column("rarity", sa.String(), nullable=True))
    op.add_column("optcg_card", sa.Column("card_set_id", sa.String(), nullable=True))
    op.add_column("optcg_card", sa.Column("card_type", sa.String(), nullable=True))
    op.add_column("optcg_card", sa.Column("card_image", sa.String(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE optcg_card AS detail
            SET
                id = identity.id,
                card_name = identity.name,
                set_name = identity.set_name,
                set_id = identity.set_code,
                rarity = identity.rarity,
                card_set_id = identity.card_number,
                card_type = identity.card_type,
                card_image = identity.image_url
            FROM card AS identity
            WHERE detail.card_id = identity.id
            """
        )
    )

    op.alter_column("optcg_card", "id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("optcg_card", "card_name", existing_type=sa.String(), nullable=False)
    op.alter_column("optcg_card", "set_name", existing_type=sa.String(), nullable=False)
    op.alter_column("optcg_card", "set_id", existing_type=sa.String(), nullable=False)
    op.alter_column("optcg_card", "rarity", existing_type=sa.String(), nullable=False)
    op.alter_column("optcg_card", "card_set_id", existing_type=sa.String(), nullable=False)
    op.alter_column("optcg_card", "card_type", existing_type=sa.String(), nullable=False)

    op.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS optcg_card_id_seq"))
    op.execute(
        sa.text(
            """
            SELECT setval(
                'optcg_card_id_seq',
                COALESCE((SELECT MAX(id) FROM optcg_card), 1),
                (SELECT EXISTS (SELECT 1 FROM optcg_card))
            )
            """
        )
    )
    op.alter_column(
        "optcg_card",
        "id",
        existing_type=sa.Integer(),
        server_default=sa.text("nextval('optcg_card_id_seq')"),
    )
    op.execute(sa.text("ALTER SEQUENCE optcg_card_id_seq OWNED BY optcg_card.id"))

    op.drop_constraint("optcg_card_pkey", "optcg_card", type_="primary")
    op.drop_constraint("fk_optcg_card_card_id", "optcg_card", type_="foreignkey")
    op.drop_column("optcg_card", "card_id")
    op.create_primary_key("optcg_card_pkey", "optcg_card", ["id"])
    op.create_unique_constraint(
        "uq_optcg_card_name_set_id",
        "optcg_card",
        ["card_name", "set_id"],
    )

    op.drop_index("ix_card_game", table_name="card")
    op.drop_table("card")
