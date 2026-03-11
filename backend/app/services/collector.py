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
from app.services.entity_extractor import extract_entities, entity_overlap
from app.config import get_settings

logger = logging.getLogger(__name__)

# In-memory caches to avoid redundant NLP calls within a collection run
_embedding_cache: dict[str, list[float] | None] = {}
_entity_cache: dict[str, set[str]] = {}


def _cached_encode(text: str) -> list[float] | None:
    """Encode text with in-memory cache to avoid repeated model calls."""
    if text not in _embedding_cache:
        _embedding_cache[text] = encode_text(text)
    return _embedding_cache[text]


def _cached_entities(text: str) -> set[str]:
    """Extract entities with in-memory cache."""
    if text not in _entity_cache:
        _entity_cache[text] = extract_entities(text)
    return _entity_cache[text]

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


def _parse_json_feed(content: str, feed_url: str) -> list[dict[str, Any]]:
    """Parse JSON feed (e.g. NHK) and return list of article dicts."""
    import json as _json

    try:
        data = _json.loads(content)
    except (ValueError, TypeError):
        return []

    # Handle both top-level array and {"data": [...]} / {"channel": {"item": [...]}}
    items: list = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("data", "items", "news", "channel"):
            candidate = data.get(key)
            if isinstance(candidate, list):
                items = candidate
                break
            if isinstance(candidate, dict):
                nested = candidate.get("item", candidate.get("items", []))
                if isinstance(nested, list):
                    items = nested
                    break

    articles = []
    for item in items[:30]:
        if not isinstance(item, dict):
            continue
        title = item.get("title", item.get("headline", ""))
        if not title:
            continue
        summary = item.get("summary", item.get("description", item.get("lead", "")))
        url = item.get("url", item.get("link", feed_url))
        # Parse date from various field names
        date_str = item.get("updated", item.get("date", item.get("pubDate", "")))
        pub = datetime.now(timezone.utc)
        if date_str:
            try:
                from email.utils import parsedate_to_datetime
                pub = parsedate_to_datetime(date_str)
            except Exception:
                try:
                    pub = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    pass
        articles.append(
            {
                "title": str(title),
                "summary": str(summary)[:500] if summary else "",
                "url": str(url),
                "event_time": pub,
                "source_name": "NHK中文",
            }
        )
    return articles


def _detect_source_type(source_name: str, url: str) -> SourceType:
    """Heuristic source type detection based on name/URL."""
    name_lower = source_name.lower()
    url_lower = url.lower()
    if any(k in name_lower or k in url_lower for k in ["gov", "政府", "官方", "国务院"]):
        return SourceType.government
    if any(k in name_lower or k in url_lower for k in [
        "新华", "人民", "央视", "xinhua", "cctv",
        "bbc", "dw", "rfi", "nyt", "nhk", "reuters", "yna", "cna", "zaobao",
        "纽约时报", "德国之声", "法广", "韩联社", "联合早报", "中央通讯社",
    ]):
        return SourceType.mainstream_media
    if any(k in name_lower or k in url_lower for k in ["学", "研究", "academic", "journal"]):
        return SourceType.academic
    if any(k in name_lower or k in url_lower for k in ["微博", "weibo", "微信", "twitter", "social"]):
        return SourceType.social_media
    return SourceType.local_media


async def _classify_to_case(db: AsyncSession, title: str, summary: str) -> str:
    """Classify an article into an existing case or create a new one.

    Two-layer strategy:
      Layer 1 — jieba entity overlap (lightweight, no model needed)
      Layer 2 — semantic cosine similarity (sentence-transformers)

    Match if: (entity_overlap >= threshold AND cosine >= 0.35)
              OR cosine >= case_similarity_threshold
    Fallback: entity overlap alone when NLP model unavailable.
    """
    settings = get_settings()
    article_text = f"{title} {summary[:200]}"
    article_embedding = _cached_encode(article_text)
    article_entities = _cached_entities(title)

    # Load all active cases
    stmt = select(Case).where(Case.status != CaseStatus.closed)
    result = await db.execute(stmt)
    cases = result.scalars().all()

    best_case: Case | None = None
    best_combined_score = 0.0

    for case in cases:
        case_entities = _cached_entities(case.title)
        overlap = entity_overlap(article_entities, case_entities)

        semantic_score = 0.0
        if article_embedding is not None:
            case_embedding = _cached_encode(case.title)
            if case_embedding is not None:
                semantic_score = _cosine_similarity(article_embedding, case_embedding)

        # Two-layer decision
        matched = False
        if overlap >= settings.case_entity_overlap_threshold and semantic_score >= 0.35:
            matched = True
        elif semantic_score >= settings.case_similarity_threshold:
            matched = True
        elif article_embedding is None and overlap >= settings.case_entity_overlap_threshold:
            # Fallback: entity overlap alone when NLP model unavailable
            matched = True

        combined = overlap + semantic_score  # for ranking best match
        logger.debug(
            "Classification: '%s' vs case '%s' → overlap=%.3f, semantic=%.3f, matched=%s",
            title[:30], case.title[:30], overlap, semantic_score, matched,
        )

        if matched and combined > best_combined_score:
            best_combined_score = combined
            best_case = case

    if best_case is not None:
        logger.info(
            "Article '%s' classified into case '%s' (combined=%.3f)",
            title[:40], best_case.title[:40], best_combined_score,
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
        if feed.url.endswith(".json"):
            articles = _parse_json_feed(content, feed.url)
        else:
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
    _embedding_cache.clear()
    _entity_cache.clear()
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
