from typing import Annotated

from fastapi import Depends

from .service import OptcgCatalogService


def get_optcg_catalog_service() -> OptcgCatalogService:
    return OptcgCatalogService()


OptcgCatalogServiceDep = Annotated[OptcgCatalogService, Depends(get_optcg_catalog_service)]
