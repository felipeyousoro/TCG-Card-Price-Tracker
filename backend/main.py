from fastapi import FastAPI

from api.main import api_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


app.include_router(api_router)
