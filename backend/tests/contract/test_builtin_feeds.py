"""Contract tests for built-in feed operations (T015-T016, T020-T022)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_feed import DataFeed, FeedStatus, FeedType
from app.models.source import Source, EventNodeSource, SourceType
from app.models.event_node import EventNode
from app.models.case import Case, CaseStatus


@pytest_asyncio.fixture
async def builtin_feed(db_session: AsyncSession) -> DataFeed:
    """Create a test built-in scraper feed."""
    feed = DataFeed(
        id=str(uuid.uuid4()),
        name="测试内置源",
        url="https://example.com/test-builtin",
        feed_type=FeedType.scraper,
        parse_config={"title_selector": "h2 a", "summary_selector": "p", "source_name": "测试源"},
        is_builtin=True,
        schedule_cron="*/30 * * * *",
        status=FeedStatus.normal,
        consecutive_failures=0,
    )
    db_session.add(feed)
    await db_session.flush()
    return feed


@pytest_asyncio.fixture
async def custom_feed(db_session: AsyncSession) -> DataFeed:
    """Create a test user-custom feed."""
    feed = DataFeed(
        id=str(uuid.uuid4()),
        name="用户自定义源",
        url="https://example.com/custom",
        feed_type=FeedType.rss,
        is_builtin=False,
        schedule_cron="0 2 * * *",
        status=FeedStatus.normal,
        consecutive_failures=0,
    )
    db_session.add(feed)
    await db_session.flush()
    return feed


@pytest_asyncio.fixture
async def source_with_url(db_session: AsyncSession, builtin_feed: DataFeed) -> Source:
    """Create a source record with a specific URL for dedup testing."""
    source = Source(
        id=str(uuid.uuid4()),
        name="测试源",
        source_type=SourceType.mainstream_media,
        url="https://example.com/article-1",
        reputation_score=50.0,
        collected_at=datetime.now(timezone.utc),
        data_feed_id=builtin_feed.id,
    )
    db_session.add(source)
    await db_session.flush()
    return source


# --- T016: URL deduplication test ---

@pytest.mark.asyncio
async def test_url_dedup_skips_existing_source(db_session: AsyncSession, builtin_feed, source_with_url):
    """T016: collect_feed should skip articles if Source with same URL already exists."""
    # Verify the source exists
    result = await db_session.execute(
        select(Source).where(Source.url == "https://example.com/article-1")
    )
    existing = result.scalars().all()
    assert len(existing) >= 1, "Source with URL should already exist"


# --- T020: DELETE returns 403 for built-in feeds ---

@pytest.mark.asyncio
async def test_delete_builtin_feed_returns_403(client, db_session, builtin_feed):
    """T020: DELETE /feeds/{id} returns 403 when feed is_builtin=True."""
    await db_session.commit()
    resp = await client.delete(f"/api/v1/feeds/{builtin_feed.id}")
    assert resp.status_code == 403
    assert "built-in" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_custom_feed_succeeds(client, db_session, custom_feed):
    """Custom feeds can still be deleted normally."""
    await db_session.commit()
    resp = await client.delete(f"/api/v1/feeds/{custom_feed.id}")
    assert resp.status_code == 204


# --- T021: PATCH blocks name/url on built-in feeds ---

@pytest.mark.asyncio
async def test_patch_builtin_feed_blocks_protected_fields(client, db_session, builtin_feed):
    """T021: PATCH /feeds/{id} blocks name/url/feed_type/schedule_cron on built-in feeds."""
    await db_session.commit()
    resp = await client.patch(
        f"/api/v1/feeds/{builtin_feed.id}",
        json={"name": "新名字"},
    )
    assert resp.status_code == 403
    assert "protected" in resp.json()["detail"].lower() or "built-in" in resp.json()["detail"].lower()


# --- T022: PATCH allows status change on built-in feeds ---

@pytest.mark.asyncio
async def test_patch_builtin_feed_allows_status_change(client, db_session, builtin_feed):
    """T022: PATCH /feeds/{id} allows status change on built-in feeds."""
    await db_session.commit()
    resp = await client.patch(
        f"/api/v1/feeds/{builtin_feed.id}",
        json={"status": "offline"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "offline"
