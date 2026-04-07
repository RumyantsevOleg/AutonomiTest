from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session, create_engine

from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_ctx() -> Generator[Session, None, None]:
    """Context manager version for use outside FastAPI (e.g. Celery tasks)."""
    with Session(engine) as session:
        yield session
