from typing import Annotated

from fastapi import Depends

from .service import FavoriteService


def get_favorite_service() -> FavoriteService:
    return FavoriteService()


FavoriteServiceDep = Annotated[FavoriteService, Depends(get_favorite_service)]
