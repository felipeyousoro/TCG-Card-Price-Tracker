from typing import Annotated

from fastapi import Depends

from .service import ProductCatalogService


def get_product_catalog_service() -> ProductCatalogService:
    return ProductCatalogService()


ProductCatalogServiceDep = Annotated[ProductCatalogService, Depends(get_product_catalog_service)]
