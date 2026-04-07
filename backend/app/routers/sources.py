from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import Source
from app.schemas import SourceRead

router = APIRouter(prefix="/api", tags=["sources"])


@router.get("/sources", response_model=list[SourceRead])
def list_sources(session: Session = Depends(get_session)):
    sources = session.exec(select(Source)).all()
    return sources
