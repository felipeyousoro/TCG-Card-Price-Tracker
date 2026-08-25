from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import CardGame


class CardRead(BaseModel):
    """Shared catalog identity row."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    game: CardGame
    name: str
    set_name: str
    set_code: str
    card_number: str
    rarity: str
    card_type: str
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = Field(default=None)


class CardListItem(BaseModel):
    """Slim shared catalog row for generic list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    game: CardGame
    name: str
    set_name: str
    set_code: str
    card_number: str
    rarity: str
    card_type: str
    image_url: str | None = None


class CardFilterOptions(BaseModel):
    """Distinct values for shared catalog filters."""

    rarities: list[str]
    set_names: list[str]
