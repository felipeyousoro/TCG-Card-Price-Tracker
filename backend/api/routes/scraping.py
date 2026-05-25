from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from core.db import SessionLocal
from data.ligaonepiece_collections import LIGAONEPIECE_COLLECTIONS
from models import Collection, OnePieceCard, OnePieceCardVersion
from services.scraping.ScrapeLigaOnePiece import ScrapeLigaOnePiece

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ScrapeListRequest(BaseModel):
    url: str | None = None
    collection: str | None = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    pages: int


class OnePieceCardOut(BaseModel):
    id: int
    code: str
    rarity: str
    collection: str

    model_config = {"from_attributes": True}


class CollectionOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


@router.get("/ligaonepiece/get_onepiece_cards", response_model=PaginatedResponse)
def get_onepiece_cards(
    collection: str | None = None,
    rarity: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(OnePieceCard).options(joinedload(OnePieceCard.collection))

    if collection:
        query = query.join(Collection).filter(Collection.name == collection)
    if rarity:
        query = query.filter(OnePieceCard.rarity == rarity)

    total = query.count()
    cards = query.offset((page - 1) * limit).limit(limit).all()

    items = [
        OnePieceCardOut(
            id=card.id,
            code=card.code,
            rarity=card.rarity,
            collection=card.collection.name,
        ).model_dump()
        for card in cards
    ]

    pages = (total + limit - 1) // limit if total else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/ligaonepiece/get_onepiece_collections", response_model=PaginatedResponse)
def get_onepiece_collections(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Collection)
    total = query.count()
    collections = query.offset((page - 1) * limit).limit(limit).all()

    items = [CollectionOut.model_validate(c).model_dump() for c in collections]
    pages = (total + limit - 1) // limit if total else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/ligaonepiece/get_scrape_collections")
def get_scrape_collections():
    return {"items": LIGAONEPIECE_COLLECTIONS}


@router.post("/ligaonepiece/scrape-collection")
# TODO: trocar pra get
async def scrape_collection_liga(request: ScrapeListRequest, db: Session = Depends(get_db)):
    try:
        url = request.url
        if request.collection:
            match = next(
                (item for item in LIGAONEPIECE_COLLECTIONS if item["collection"] == request.collection),
                None,
            )
            if not match:
                raise HTTPException(status_code=404, detail=f"Collection '{request.collection}' not found")
            url = match["url"]

        if not url:
            raise HTTPException(status_code=400, detail="Provide either 'collection' or 'url'")

        scraper = ScrapeLigaOnePiece(session=db)
        scraper.scrape_collection(url)
        collection_name = request.collection or url
        return {
            "status": "success",
            "message": f"Collection '{collection_name}' scraped and inserted successfully",
        }
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ligaonepiece/scrape-by-rarity")
async def scrape_by_rarity_ligaonepiece(rarity: str = "SR", db: Session = Depends(get_db)):
    try:
        cards = (
            db.query(OnePieceCardVersion)
            .join(OnePieceCardVersion.card)
            .filter(OnePieceCard.rarity == rarity)
            .all()
        )
        scraper = ScrapeLigaOnePiece(session=db)
        for card in cards:
            scraper.scrape_card(card)
        return {"status": "success", "message": f"Scraped {len(cards)} cards with rarity {rarity}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ligaonepiece/scrape-card/{card_id}")
async def scrape_card_liga(card_id: int, db: Session = Depends(get_db)):
    try:
        card = db.get(OnePieceCardVersion, card_id)
        scraper = ScrapeLigaOnePiece(session=db)
        scraper.scrape_card(card)
        return {"status": "success", "message": "Card data scraped and inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
