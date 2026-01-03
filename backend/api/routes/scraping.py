from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db import SessionLocal
from services.scraping.scrap_liga import ScrapLiga

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ScrapListRequest(BaseModel):
    url: str

@router.post("/scrap-list-liga")
async def scrap_liga_endpoint(request: ScrapListRequest, db: Session = Depends(get_db)):
    try:
        scraper = ScrapLiga(session=db)
        scraper.scrap_and_insert(request.url)
        return {"status": "success", "message": "Data scraped and inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

