from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.db import SessionLocal
from models import OnePieceCardVersion
from services.scraping.ScrapLiga import ScrapLiga

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ScrapListRequest(BaseModel):
    url: str


@router.post("/liga/scrap-collection")
# TODO: trocar pra get
async def scrap_collection_liga(request: ScrapListRequest, db: Session = Depends(get_db)):
    try:
        scraper = ScrapLiga(session=db)
        scraper.scrap_collection(request.url)
        return {"status": "success", "message": "Data scraped and inserted successfully"}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/liga/scrap-card")
async def scrap_all_cards(db: Session = Depends(get_db)):
    try:
        all_cards = db.query(OnePieceCardVersion).all()
        for card in all_cards:
            scraper = ScrapLiga(session=db)
            scraper.scrap_card(card)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/liga/scrap-card/{card_id}")
async def scrap_card_liga(card_id: int, db: Session = Depends(get_db)):
    try:
        card = db.get(OnePieceCardVersion, card_id)
        scraper = ScrapLiga(session=db)
        scraper.scrap_card(card)
        return {"status": "success", "message": "Card data scraped and inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
