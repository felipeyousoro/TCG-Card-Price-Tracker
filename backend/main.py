from typing import Union

from api.main import api_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(api_router, prefix="/api")
