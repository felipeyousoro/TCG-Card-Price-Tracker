from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y")


def _parse_optcg_date(value: object) -> object:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return value
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return value


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

    @field_validator("date_scraped", mode="before")
    @classmethod
    def parse_date_scraped(cls, value: object) -> object:
        return _parse_optcg_date(value)
