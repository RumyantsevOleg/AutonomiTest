"""Initial schema - sources, articles, chat_messages

Revision ID: 001
Revises:
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("rss_url", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "source_id",
            sa.Integer(),
            sa.ForeignKey("sources.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("original_title", sa.String(), nullable=False),
        sa.Column("original_description", sa.String(), nullable=False),
        sa.Column("original_url", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("fake_title", sa.String(), nullable=True),
        sa.Column("fake_description", sa.String(), nullable=True),
        sa.Column(
            "transform_status",
            sa.Enum("pending", "processing", "completed", "failed", name="transformstatus"),
            nullable=False,
            server_default="pending",
            index=True,
        ),
        sa.Column("transformed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("articles")
    op.drop_table("sources")
