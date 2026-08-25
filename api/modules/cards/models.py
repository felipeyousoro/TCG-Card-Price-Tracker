from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database.models import TimestampMixin
from ...core.database.session import Base

if TYPE_CHECKING:
    from ..optcg.models import OptcgCard


class Card(Base, TimestampMixin):
    """Universal card identity shared across every supported game."""

    __tablename__ = "card"
    __table_args__ = (
        UniqueConstraint(
            "game",
            "name",
            "set_code",
            name="uq_card_game_name_set_code",
        ),
    )

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        nullable=False,
        primary_key=True,
        init=False,
    )

    game: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String)
    set_name: Mapped[str] = mapped_column(String)
    set_code: Mapped[str] = mapped_column(String)
    card_number: Mapped[str] = mapped_column(String)
    rarity: Mapped[str] = mapped_column(String)
    card_type: Mapped[str] = mapped_column(String)
    image_url: Mapped[str | None] = mapped_column(String, default=None)

    optcg_detail: Mapped["OptcgCard | None"] = relationship(
        "OptcgCard",
        back_populates="card",
        uselist=False,
        init=False,
        default=None,
    )
