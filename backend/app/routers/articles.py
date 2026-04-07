from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, select

from app.database import get_session
from app.models import Article, TransformStatus
from app.schemas import ArticleRead

router = APIRouter(prefix="/api", tags=["articles"])


@router.get("/articles", response_model=list[ArticleRead])
def list_articles(
    source_id: int | None = None,
    status: TransformStatus | None = TransformStatus.completed,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    stmt = (
        select(Article)
        .options(selectinload(Article.source))
        .order_by(col(Article.created_at).desc())
    )
    if source_id:
        stmt = stmt.where(Article.source_id == source_id)
    if status:
        stmt = stmt.where(Article.transform_status == status)
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    articles = session.exec(stmt).all()
    return articles


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, session: Session = Depends(get_session)):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
