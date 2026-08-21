from datetime import date

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database.models import TimestampMixin
from ...core.database.session import Base


class OptcgCard(Base, TimestampMixin):
    """One Piece TCG card scraped from an official or third-party source."""

    __tablename__ = "optcg_card"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        nullable=False,
        primary_key=True,
        init=False,
    )

    card_name: Mapped[str] = mapped_column(String)
    set_name: Mapped[str] = mapped_column(String)
    set_id: Mapped[str] = mapped_column(String)
    rarity: Mapped[str] = mapped_column(String)
    card_set_id: Mapped[str] = mapped_column(String)
    card_type: Mapped[str] = mapped_column(String)
    date_scraped: Mapped[date] = mapped_column(Date)

    card_text: Mapped[str | None] = mapped_column(Text, default=None)
    card_color: Mapped[str | None] = mapped_column(String, default=None)
    life: Mapped[str | None] = mapped_column(String, default=None)
    card_cost: Mapped[str | None] = mapped_column(String, default=None)
    card_power: Mapped[str | None] = mapped_column(String, default=None)
    sub_types: Mapped[str | None] = mapped_column(String, default=None)
    counter_amount: Mapped[int | None] = mapped_column(Integer, default=None)
    attribute: Mapped[str | None] = mapped_column(String, default=None)
    card_image_id: Mapped[str | None] = mapped_column(String, default=None)
    card_image: Mapped[str | None] = mapped_column(String, default=None)
