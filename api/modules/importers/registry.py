from ...common.exceptions import ValidationError
from ...core.config.settings import get_settings
from ...modules.optcg.service import OptcgCatalogService
from .base import OptcgImporter
from .optcgapi.client import OptcgApiClient
from .optcgapi.importer import OptcgApiImporter

_IMPORTER_CATALOG: tuple[dict[str, str], ...] = (
    {
        "source": "optcgapi",
        "label": "optcgapi",
        "description": "Import the full OPTCG card catalog from optcgapi.com.",
    },
)

_KNOWN_SOURCES = tuple(item["source"] for item in _IMPORTER_CATALOG)


def list_importer_catalog() -> tuple[dict[str, str], ...]:
    """Return static metadata for every registered importer source."""
    return _IMPORTER_CATALOG


def get_importer(source: str) -> OptcgImporter:
    """Build an OPTCG importer by source key."""
    normalized = source.strip().lower()
    if normalized == OptcgApiImporter.source:
        settings = get_settings()
        return OptcgApiImporter(
            client=OptcgApiClient(
                base_url=settings.OPTCGAPI_BASE_URL,
                timeout=settings.OPTCGAPI_TIMEOUT_SECONDS,
            ),
            catalog=OptcgCatalogService(),
        )

    known = ", ".join(_KNOWN_SOURCES)
    raise ValidationError(f"Unknown importer source '{source}'. Known sources: {known}")
