import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database.models import TimestampMixin
from ...core.database.session import Base

XOR_CARD_PRODUCT = (
    "(card_id IS NOT NULL AND product_id IS NULL) OR (card_id IS NULL AND product_id IS NOT NULL)"
)


class Favorite(Base, TimestampMixin):
    """A user's starred card or product."""

    __tablename__ = "favorite"
    __table_args__ = (
        CheckConstraint(XOR_CARD_PRODUCT, name="ck_favorite_card_xor_product"),
        Index(
            "uq_favorite_user_card",
            "user_id",
            "card_id",
            unique=True,
            postgresql_where=text("card_id IS NOT NULL"),
        ),
        Index(
            "uq_favorite_user_product",
            "user_id",
            "product_id",
            unique=True,
            postgresql_where=text("product_id IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default_factory=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        init=False,
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    card_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("card.id"),
        default=None,
        index=True,
    )
    product_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        default=None,
        index=True,
    )
