import datetime
from enum import Enum

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel


class TransformStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    rss_url: str
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

    articles: list["Article"] = Relationship(back_populates="source")


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="sources.id", index=True)

    # Original content
    original_title: str
    original_description: str
    original_url: str = Field(unique=True, index=True)
    published_at: datetime.datetime | None = None

    # Satirical content (NULL until transformed)
    fake_title: str | None = None
    fake_description: str | None = None

    # Pipeline status
    transform_status: TransformStatus = Field(
        default=TransformStatus.pending, index=True
    )
    transformed_at: datetime.datetime | None = None

    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    updated_at: datetime.datetime = Field(
        sa_column=sa.Column(
            sa.DateTime,
            default=lambda: datetime.datetime.now(datetime.UTC),
            onupdate=lambda: datetime.datetime.now(datetime.UTC),
            nullable=False,
        )
    )

    source: Source | None = Relationship(back_populates="articles")
    chat_messages: list["ChatMessage"] = Relationship(back_populates="article")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: int | None = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="articles.id", index=True)
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

    article: Article | None = Relationship(back_populates="chat_messages")
