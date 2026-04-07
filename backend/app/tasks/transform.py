import datetime

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.database import get_session_ctx
from app.models import Article, TransformStatus
from app.services.transformer import transform_article_content
from app.tasks.celery_app import celery


@celery.task(bind=True, max_retries=3)
def transform_article(self, article_id: int):
    with get_session_ctx() as session:
        article = session.exec(
            select(Article)
            .options(selectinload(Article.source))
            .where(Article.id == article_id)
        ).first()
        if not article:
            return

        article.transform_status = TransformStatus.processing
        session.add(article)
        session.commit()

        try:
            source_name = article.source.name if article.source else "Unknown"
            result = transform_article_content(
                title=article.original_title,
                description=article.original_description,
                source_name=source_name,
            )
            article.fake_title = result["title"]
            article.fake_description = result["description"]
            article.transform_status = TransformStatus.completed
            article.transformed_at = datetime.datetime.now(datetime.UTC)
        except Exception as exc:
            article.transform_status = TransformStatus.failed
            session.add(article)
            session.commit()
            raise self.retry(exc=exc, countdown=10 * (2**self.request.retries))

        session.add(article)
        session.commit()
