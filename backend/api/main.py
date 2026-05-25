from fastapi import APIRouter
from api.routes import scraping

api_router = APIRouter()

api_router.include_router(scraping.router, tags=["scraping"])
