"""Data collector service — RSS (feedparser) + HTML scraping (httpx + BS4).

FR-001: Support ≥2 public data source types (RSS + HTML scraper).
FR-002: Structuralise raw data into standard event format.
FR-015: Mark DataFeed as 'warning' after 3 consecutive failures.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.case import Case, CaseStatus
from app.models.data_feed import DataFeed, FeedStatus
from app.models.event_node import EventNode
from app.models.source import EventNodeSource, Source, SourceType
from app.services.nlp_matcher import encode_text, find_matching_event

logger = logging.getLogger(__name__)

RETRY_DELAYS = [1, 2, 4]  # exponential backoff in seconds
REQUEST_DELAY = 2.0  # polite crawl delay


async def _fetch_url(url: str, retries: int = 3) -> str | None:
    """Fetch URL content with retry/exponential backoff. Respects REQUEST_DELAY."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for attempt, delay in enumerate(RETRY_DELAYS[:retries], 1):
            try:
                resp = await client.get(url, headers={"User-Agent": "PostTruthBot/0.1"})
                resp.raise_for_status()
                await asyncio.sleep(REQUEST_DELAY)
                return resp.text
            except Exception as exc:
                logger.warning("Fetch attempt %d/%d failed for %s: %s", attempt, retries, url, exc)
                if attempt < retries:
                    await asyncio.sleep(delay)
    return None


def _parse_rss(content: str, feed_url: str) -> list[dict[str, Any]]:
    """Parse RSS/Atom feed and return list of article dicts."""
    parsed = feedparser.parse(content)
    articles = []
    for entry in parsed.entries:
        pub: datetime = datetime.now(timezone.utc)
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            import time
            pub = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        articles.append(
            {
                "title": getattr(entry, "title", "无标题"),
                "summary": getattr(entry, "summary", getattr(entry, "description", "")),
                "url": getattr(entry, "link", feed_url),
                "event_time": pub,
                "source_name": parsed.feed.get("title", "Unknown"),
            }
        )
    return articles


def _parse_html(content: str, base_url: str, parse_config: dict | None) -> list[dict[str, Any]]:
    """Parse HTML page using CSS selectors from parse_config."""
    if not parse_config:
        return []
    soup = BeautifulSoup(content, "lxml")
    title_sel = parse_config.get("title_selector", "h1")
    summary_sel = parse_config.get("summary_selector", "p")
    articles = []
    titles = soup.select(title_sel)
    summaries = soup.select(summary_sel)
    for i, t in enumerate(titles[:20]):
        summary_text = summaries[i].get_text(" ", strip=True) if i < len(summaries) else ""
        articles.append(
            {
                "title": t.get_text(strip=True),
                "summary": summary_text[:500],
                "url": base_url,
                "event_time": datetime.now(timezone.utc),
                "source_name": parse_config.get("source_name", "Unknown"),
            }
        )
    return articles


def _detect_source_type(source_name: str, url: str) -> SourceType:
    """Heuristic source type detection based on name/URL."""
    name_lower = source_name.lower()
    url_lower = url.lower()
    if any(k in name_lower or k in url_lower for k in ["gov", "政府", "官方", "国务院"]):
        return SourceType.government
    if any(k in name_lower or k in url_lower for k in ["新华", "人民", "央视", "xinhua", "cctv"]):
        return SourceType.mainstream_media
    if any(k in name_lower or k in url_lower for k in ["学", "研究", "academic", "journal"]):
        return SourceType.academic
    if any(k in name_lower or k in url_lower for k in ["微博", "weibo", "微信", "twitter", "social"]):
        return SourceType.social_media
    return SourceType.local_media


CASE_SIMILARITY_THRESHOLD = 0.55  # lower than event dedup — topic-level grouping


async def _classify_to_case(db: AsyncSession, title: str, summary: str) -> str:
    """Classify an article into an existing case or create a new one.

    Uses NLP embedding of the article title+summary and compares against
    all active case titles. If similarity >= CASE_SIMILARITY_THRESHOLD,
    the article joins that case; otherwise a new case is created.
    """
    article_text = f"{title} {summary[:200]}"
    article_embedding = encode_text(article_text)

    # If NLP model unavailable, create one case per article title
    if article_embedding is None:
        return await _create_case_from_article(db, title, summary)

    # Load all active cases
    stmt = select(Case).where(Case.status != CaseStatus.closed)
    result = await db.execute(stmt)
    cases = result.scalars().all()

    best_case: Case | None = None
    best_score = 0.0

    for case in cases:
        # Encode case title for comparison
        case_embedding = encode_text(case.title)
        if case_embedding is None:
            continue
        score = _cosine_similarity(article_embedding, case_embedding)
        logger.debug(
            "Classification: '%s' vs case '%s' → score=%.3f (threshold=%.2f)",
            title[:30], case.title[:30], score, CASE_SIMILARITY_THRESHOLD,
        )
        if score >= CASE_SIMILARITY_THRESHOLD and score > best_score:
            best_score = score
            best_case = case

    if best_case is not None:
        logger.info(
            "Article '%s' classified into case '%s' (score=%.3f)",
            title[:40], best_case.title[:40], best_score,
        )
        return best_case.id

    # No matching case — create a new one
    return await _create_case_from_article(db, title, summary)


async def _create_case_from_article(db: AsyncSession, title: str, summary: str) -> str:
    """Create a new case from an article's title."""
    case = Case(
        id=str(uuid.uuid4()),
        title=title[:200],
        description=summary[:500] if summary else title,
        status=CaseStatus.active,
    )
    db.add(case)
    await db.flush()
    logger.info("Created new case: '%s'", title[:60])
    return case.id


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity helper."""
    import numpy as np
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    na, nb = np.linalg.norm(va), np.linalg.norm(vb)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(va, vb) / (na * nb))


async def collect_feed(feed: DataFeed) -> bool:
    """Run collection for a single DataFeed. Returns True on success."""
    logger.info("Collecting feed: %s [%s]", feed.name, feed.feed_type)
    content = await _fetch_url(feed.url)
    if content is None:
        logger.error("Failed to fetch feed: %s", feed.name)
        return False

    if feed.feed_type.value == "rss":
        articles = _parse_rss(content, feed.url)
    else:
        articles = _parse_html(content, feed.url, feed.parse_config)

    if not articles:
        logger.warning("No articles extracted from feed: %s", feed.name)
        return True  # not a failure — just empty

    async with AsyncSessionLocal() as db:
        for art in articles:
            title: str = art["title"][:300]
            summary: str = art["summary"][:2000] if art["summary"] else title
            url: str = art["url"]
            event_time: datetime = art["event_time"]
            source_name: str = art["source_name"]

            # URL deduplication — skip if a Source with the same URL already exists
            existing_source = await db.execute(
                select(Source).where(Source.url == url)
            )
            if existing_source.scalar_one_or_none() is not None:
                logger.debug("Skipping duplicate URL: %s", url[:80])
                continue

            # Auto-classify into existing or new case by topic similarity
            case_id = await _classify_to_case(db, title, summary)

            # NLP dedup — find or create event node
            existing_node = await find_matching_event(db, case_id, title, summary, event_time)

            if existing_node is None:
                embedding = encode_text(f"{title} {summary}")
                node = EventNode(
                    id=str(uuid.uuid4()),
                    case_id=case_id,
                    title=title,
                    summary=summary,
                    event_time=event_time,
                    embedding_json=__import__("json").dumps(embedding) if embedding else None,
                )
                db.add(node)
                await db.flush()
                node_id = node.id
            else:
                node_id = existing_node.id

            # Create source
            source = Source(
                id=str(uuid.uuid4()),
                name=source_name,
                source_type=_detect_source_type(source_name, url),
                url=url,
                reputation_score=50.0,
                collected_at=datetime.now(timezone.utc),
                data_feed_id=feed.id,
            )
            db.add(source)
            await db.flush()

            # Associate source with event node
            assoc = EventNodeSource(
                event_node_id=node_id,
                source_id=source.id,
                raw_content=summary[:500],
            )
            db.add(assoc)

        await db.commit()
        logger.info("Feed '%s': saved %d articles.", feed.name, len(articles))
    return True


async def run_collection_for_feed(feed_id: str) -> None:
    """Called by scheduler or manual trigger; updates feed health state."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
        feed = result.scalar_one_or_none()
        if feed is None or feed.status == FeedStatus.offline:
            return

        success = await collect_feed(feed)

        if success:
            feed.consecutive_failures = 0
            feed.status = FeedStatus.normal
            feed.last_collected_at = datetime.now(timezone.utc)
        else:
            feed.consecutive_failures += 1
            if feed.consecutive_failures >= 3:
                feed.status = FeedStatus.warning

        await db.commit()
