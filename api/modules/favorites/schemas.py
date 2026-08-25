from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FavoriteCreate(BaseModel):
    """Star a card or a product."""

    model_config = ConfigDict(extra="forbid")

    card_id: int | None = None
    product_id: int | None = None

    @model_validator(mode="after")
    def exactly_one_item(self) -> "FavoriteCreate":
        if (self.card_id is None) == (self.product_id is None):
            raise ValueError("Exactly one of card_id or product_id must be set")
        return self


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    card_id: int | None = None
    product_id: int | None = None
    name: str
    code: str | None = None
    image_url: str | None = None
    created_at: datetime


class FavoriteIds(BaseModel):
    card_ids: list[int] = Field(default_factory=list)
    product_ids: list[int] = Field(default_factory=list)
