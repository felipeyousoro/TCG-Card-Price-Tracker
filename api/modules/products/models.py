from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database.models import TimestampMixin
from ...core.database.session import Base

if TYPE_CHECKING:
    pass


class Product(Base, TimestampMixin):
    """Shared sealed-product catalog row. User-contributed, visible to everyone."""

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        nullable=False,
        primary_key=True,
        init=False,
    )

    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String(20), index=True)
    set_name: Mapped[str | None] = mapped_column(String, default=None)
    image_url: Mapped[str | None] = mapped_column(String, default=None)
    created_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        default=None,
        index=True,
    )
