from ...common.exceptions import ValidationError
from ...core.config.settings import get_settings
from ...modules.optcg.service import OptcgCatalogService
from .base import OptcgImporter
from .tcgplayer.api.tcgcsv.client import TcgcsvClient
from .tcgplayer.importer import TcgcsvImporter

_IMPORTER_CATALOG: tuple[dict[str, str], ...] = (
    {
        "source": "tcgcsv",
        "label": "TCGCSV",
        "description": "Import OPTCG catalog products from tcgcsv.com TCGPlayer groups.",
    },
)

_KNOWN_SOURCES = tuple(item["source"] for item in _IMPORTER_CATALOG)


def list_importer_catalog() -> tuple[dict[str, str], ...]:
    """Return static metadata for every registered importer source."""
    return _IMPORTER_CATALOG


def get_importer(source: str) -> OptcgImporter:
    """Build an OPTCG importer by source key."""
    normalized = source.strip().lower()
    if normalized == TcgcsvImporter.source:
        settings = get_settings()
        return TcgcsvImporter(
            client=TcgcsvClient(
                base_url=settings.TCGCSV_BASE_URL,
                timeout=settings.TCGCSV_TIMEOUT_SECONDS,
            ),
            catalog=OptcgCatalogService(),
        )

    known = ", ".join(_KNOWN_SOURCES)
    raise ValidationError(f"Unknown importer source '{source}'. Known sources: {known}")
