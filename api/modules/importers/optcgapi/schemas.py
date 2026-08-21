from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class OptcgApiCard(BaseModel):
    """Raw card payload from optcgapi.com /api/allSetCards/."""

    model_config = ConfigDict(extra="ignore")

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
    inventory_price: float | None = Field(default=None)
    market_price: float | None = Field(default=None)
