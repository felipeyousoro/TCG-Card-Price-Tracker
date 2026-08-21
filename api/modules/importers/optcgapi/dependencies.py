from typing import Annotated

from fastapi import Depends

from ....core.config.settings import get_settings
from ....modules.optcg.dependencies import OptcgCatalogServiceDep
from .client import OptcgApiClient
from .importer import OptcgApiImporter


def get_optcgapi_client() -> OptcgApiClient:
    settings = get_settings()
    return OptcgApiClient(
        base_url=settings.OPTCGAPI_BASE_URL,
        timeout=settings.OPTCGAPI_TIMEOUT_SECONDS,
    )


def get_optcgapi_importer(
    client: Annotated[OptcgApiClient, Depends(get_optcgapi_client)],
    catalog: OptcgCatalogServiceDep,
) -> OptcgApiImporter:
    return OptcgApiImporter(client=client, catalog=catalog)


OptcgApiImporterDep = Annotated[OptcgApiImporter, Depends(get_optcgapi_importer)]
