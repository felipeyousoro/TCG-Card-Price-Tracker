import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError as PydanticValidationError

from ....common.exceptions import ValidationError

_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "optcg_groups.json"


class TcgplayerGroup(BaseModel):
    """One TCGPlayer catalog group from the curated OPTCG fixture list."""

    model_config = ConfigDict(extra="forbid")

    name: str
    category_id: int
    group_id: int
    enabled: bool = True


def load_optcg_groups(*, enabled_only: bool = False) -> list[TcgplayerGroup]:
    """Load and validate the curated OPTCG TCGPlayer groups fixture."""
    try:
        raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"TCGPlayer groups fixture is missing: {_FIXTURE_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError("TCGPlayer groups fixture is not valid JSON") from exc

    if not isinstance(raw, list):
        raise ValidationError("TCGPlayer groups fixture must be a JSON list")

    groups: list[TcgplayerGroup] = []
    seen: set[tuple[int, int]] = set()
    for index, item in enumerate(raw):
        try:
            group = TcgplayerGroup.model_validate(item)
        except PydanticValidationError as exc:
            raise ValidationError(
                f"Invalid TCGPlayer group at index {index}: {exc}"
            ) from exc
        key = (group.category_id, group.group_id)
        if key in seen:
            raise ValidationError(
                f"Duplicate TCGPlayer group {group.category_id}/{group.group_id}"
            )
        seen.add(key)
        groups.append(group)

    if enabled_only:
        return [group for group in groups if group.enabled]
    return groups
