from fastapi import APIRouter
from api.routes import scraping

api_router = APIRouter()

api_router.include_router(scraping.router, tags=["scraping"])
# api_router.include_router(login.router)
# api_router.include_router(users.router)
# api_router.include_router(utils.router)
# api_router.include_router(items.router)

#
# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)