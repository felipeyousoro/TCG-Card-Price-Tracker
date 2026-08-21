from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class OptcgCardBase(BaseModel):
    card_name: str
    set_name: str
    set_id: str
    rarity: str
    card_set_id: str
    card_type: str
    date_scraped: date
    card_text: str | None = None
    card_color: str | None = None
    life: str | None = None
    card_cost: str | None = None
    card_power: str | None = None
    sub_types: str | None = None
    counter_amount: int | None = None
    attribute: str | None = None
    card_image_id: str | None = None
    card_image: str | None = None


class OptcgCardCreate(OptcgCardBase):
    """Schema for inserting an OPTCG card."""

    model_config = ConfigDict(extra="forbid")


class OptcgCardUpdate(BaseModel):
    """Schema for partial OPTCG card updates."""

    model_config = ConfigDict(extra="forbid")

    card_name: str | None = None
    set_name: str | None = None
    set_id: str | None = None
    rarity: str | None = None
    card_set_id: str | None = None
    card_type: str | None = None
    date_scraped: date | None = None
    card_text: str | None = None
    card_color: str | None = None
    life: str | None = None
    card_cost: str | None = None
    card_power: str | None = None
    sub_types: str | None = None
    counter_amount: int | None = None
    attribute: str | None = None
    card_image_id: str | None = None
    card_image: str | None = None


class OptcgCardRead(OptcgCardBase):
    """Schema for reading an OPTCG card."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime | None = Field(default=None)


class OptcgCardListItem(BaseModel):
    """Slim catalog row for the cards grid."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    card_name: str
    card_set_id: str
    card_image: str | None = None


class OptcgCardFilterOptions(BaseModel):
    """Distinct values for catalog list filters."""

    colors: list[str]
    rarities: list[str]
    set_names: list[str]
