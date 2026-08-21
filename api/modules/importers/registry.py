from ...common.exceptions import ValidationError
from ...core.config.settings import get_settings
from ...modules.optcg.service import OptcgCatalogService
from .base import OptcgImporter
from .optcgapi.client import OptcgApiClient
from .optcgapi.importer import OptcgApiImporter

_KNOWN_SOURCES = ("optcgapi",)


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
