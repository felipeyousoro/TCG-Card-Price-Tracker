from datetime import date

from ......modules.optcg.schemas import OptcgCardCreate
from .schemas import TcgcsvExtendedField, TcgcsvProduct

_EMPTY = {"", "NULL", "null"}


def _extended_map(fields: list[TcgcsvExtendedField]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for field in fields:
        if field.value is None:
            continue
        text = field.value.strip()
        if text in _EMPTY:
            continue
        mapped[field.name] = text
    return mapped


def to_card_create(payload: dict[str, object], set_name: str) -> OptcgCardCreate:
    """Map a TCGCSV product dict onto the shared OPTCG create schema."""
    source = TcgcsvProduct.model_validate(payload)
    extra = _extended_map(source.extended_data)
    return OptcgCardCreate(
        card_name=source.name,
        set_name=set_name,
        tcgplayer_id=source.product_id,
        rarity=extra.get("Rarity") or "",
        card_set_id=extra.get("Number") or "",
        card_type=extra.get("CardType") or "",
        date_scraped=date.today(),
        card_text=extra.get("Description"),
        card_color=extra.get("Color"),
        card_cost=extra.get("Cost"),
        card_power=extra.get("Power"),
        sub_types=extra.get("Subtypes"),
        attribute=extra.get("Attribute"),
        card_image=source.image_url,
    )
