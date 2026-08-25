from typing import Annotated

from fastapi import Depends

from .service import CardCatalogService


def get_card_catalog_service() -> CardCatalogService:
    return CardCatalogService()


CardCatalogServiceDep = Annotated[CardCatalogService, Depends(get_card_catalog_service)]
