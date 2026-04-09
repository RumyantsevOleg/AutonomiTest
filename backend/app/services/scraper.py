import asyncio
import datetime
import html
import re
from email.utils import parsedate_to_datetime

import feedparser
import httpx
from sqlmodel import Session, select

from app.models import Article, Source, TransformStatus
from app.tasks.transform import transform_article

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_html(text: str) -> str:
    """Remove HTML tags, unescape entities, and collapse whitespace.

    RSS feeds (Guardian, NYT, NPR) return descriptions with mixed HTML —
    ``<p>``, ``<a>``, ``&amp;``, etc. We normalize on ingestion so the DB
    holds clean plain text, and both the LLM transformer and the frontend
    don't need to deal with markup.
    """
    if not text:
        return ""
    cleaned = _HTML_TAG_RE.sub("", text)
    cleaned = html.unescape(cleaned)
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


def _parse_pub_date(entry: dict) -> datetime.datetime | None:
    """Parse publication date from RSS entry, trying common fields."""
    for key in ("published", "updated", "created"):
        raw = entry.get(key)
        if raw:
            try:
                return parsedate_to_datetime(raw)
            except (ValueError, TypeError):
                pass
    # feedparser also provides *_parsed as time.struct_time
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return datetime.datetime(*parsed[:6], tzinfo=datetime.UTC)
            except (ValueError, TypeError):
                pass
    return None

FEEDS = [
    {
        "name": "New York Times",
        "rss_url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    },
    {
        "name": "NPR News",
        "rss_url": "https://feeds.npr.org/1001/rss.xml",
    },
    {
        "name": "The Guardian",
        "rss_url": "https://www.theguardian.com/world/rss",
    },
]


async def fetch_feed(url: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    return feed.entries


async def scrape_all(session: Session) -> dict:
    # Ensure sources exist
    sources = {}
    for feed_info in FEEDS:
        stmt = select(Source).where(Source.rss_url == feed_info["rss_url"])
        source = session.exec(stmt).first()
        if not source:
            source = Source(name=feed_info["name"], rss_url=feed_info["rss_url"])
            session.add(source)
            session.commit()
            session.refresh(source)
        sources[feed_info["rss_url"]] = source

    # Fetch all feeds in parallel
    results = await asyncio.gather(
        *[fetch_feed(f["rss_url"]) for f in FEEDS],
        return_exceptions=True,
    )

    new_article_ids = []
    for feed_info, entries in zip(FEEDS, results):
        if isinstance(entries, Exception):
            continue

        source = sources[feed_info["rss_url"]]
        for entry in entries:
            url = entry.get("link", "")
            if not url:
                continue

            # Dedup check
            existing = session.exec(
                select(Article).where(Article.original_url == url)
            ).first()
            if existing:
                continue

            article = Article(
                source_id=source.id,
                original_title=_strip_html(entry.get("title", "")),
                original_description=_strip_html(
                    entry.get("summary", entry.get("description", ""))
                ),
                original_url=url,
                published_at=_parse_pub_date(entry),
                transform_status=TransformStatus.pending,
            )
            session.add(article)
            session.commit()
            session.refresh(article)
            new_article_ids.append(article.id)

    # Enqueue transform jobs
    for article_id in new_article_ids:
        transform_article.delay(article_id)

    return {
        "articles_scraped": len(new_article_ids),
        "jobs_enqueued": len(new_article_ids),
    }
