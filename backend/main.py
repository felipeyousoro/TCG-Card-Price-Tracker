from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.main import api_router

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}


app.include_router(api_router)
