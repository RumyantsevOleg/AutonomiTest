import datetime

from pydantic import BaseModel

from app.models import TransformStatus


class ScrapeResponse(BaseModel):
    articles_scraped: int
    jobs_enqueued: int


class SourceRead(BaseModel):
    id: int
    name: str
    rss_url: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class ArticleRead(BaseModel):
    id: int
    source_id: int
    original_title: str
    original_description: str
    original_url: str
    published_at: datetime.datetime | None
    fake_title: str | None
    fake_description: str | None
    transform_status: TransformStatus
    transformed_at: datetime.datetime | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    source: SourceRead | None = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str


class ChatMessageRead(BaseModel):
    id: int
    article_id: int
    role: str
    content: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    role: str
    content: str
