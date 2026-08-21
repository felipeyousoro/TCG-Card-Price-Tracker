from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database.models import SoftDeleteMixin, TimestampMixin
from ...core.database.session import Base


# if TYPE_CHECKING:
#     from ..tier.models import Tier


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model representing application users."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(100))

    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")

    # tier_id: Mapped[int | None] = mapped_column(
    #     Integer,
    #     ForeignKey("tiers.id"),
    #     index=True,
    #     default=None,
    # )
    #
    # is_superuser: Mapped[bool] = mapped_column(default=False)
    #
    # tier: Mapped["Tier | None"] = relationship("Tier", back_populates="users", lazy="selectin", init=False)

    def __repr__(self) -> str:
        return f"{self.name} ({self.username})"
