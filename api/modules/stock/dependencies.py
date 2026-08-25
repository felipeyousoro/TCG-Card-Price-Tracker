from typing import Annotated

from fastapi import Depends

from .service import StockService


def get_stock_service() -> StockService:
    return StockService()


StockServiceDep = Annotated[StockService, Depends(get_stock_service)]
