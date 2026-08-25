from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database.models import TimestampMixin
from ...core.database.session import Base
from ..cards.models import Card


class OptcgCard(Base, TimestampMixin):
    """One Piece TCG fields that do not belong on the shared card identity."""

    __tablename__ = "optcg_card"

    card_id: Mapped[int] = mapped_column(
        ForeignKey("card.id", ondelete="CASCADE"),
        primary_key=True,
    )

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

    card: Mapped[Card] = relationship(back_populates="optcg_detail", init=False)
