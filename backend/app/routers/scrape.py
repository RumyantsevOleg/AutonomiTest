from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas import ScrapeResponse
from app.services.scraper import scrape_all

router = APIRouter(prefix="/api", tags=["scrape"])


@router.post("/scrape", response_model=ScrapeResponse)
async def trigger_scrape(session: Session = Depends(get_session)):
    result = await scrape_all(session)
    return result
