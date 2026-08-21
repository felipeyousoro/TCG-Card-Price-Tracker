from ....modules.optcg.schemas import OptcgCardCreate
from .schemas import OptcgApiCard

_SENTINEL_NULLS = {"NULL", "null", ""}


def _nullish(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, str) and value.strip() in _SENTINEL_NULLS:
        return None
    return value


def to_card_create(payload: dict[str, object]) -> OptcgCardCreate:
    """Map an optcgapi card dict onto the shared OPTCG create schema."""
    normalized = {key: _nullish(value) for key, value in payload.items()}
    source = OptcgApiCard.model_validate(normalized)
    return OptcgCardCreate.model_validate(
        source.model_dump(exclude={"inventory_price", "market_price"}),
    )
