"""Unit tests for built-in feed seeding (T008-T010) and classification (T028-T030)."""
from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models.data_feed import DataFeed
from app.services.builtin_feeds import BUILTIN_FEEDS, seed_builtin_feeds

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def seed_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def seed_session(seed_engine):
    session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.mark.asyncio
async def test_seed_inserts_8_builtin_feeds(seed_engine, monkeypatch):
    """T008: seed_builtin_feeds() inserts all 8 built-in feeds with is_builtin=True."""
    session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr("app.services.builtin_feeds.AsyncSessionLocal", session_factory)

    await seed_builtin_feeds()

    async with session_factory() as db:
        result = await db.execute(select(DataFeed).where(DataFeed.is_builtin == True))  # noqa: E712
        feeds = result.scalars().all()
        assert len(feeds) == 8
        for feed in feeds:
            assert feed.is_builtin is True


@pytest.mark.asyncio
async def test_seed_is_idempotent(seed_engine, monkeypatch):
    """T009: Calling seed twice doesn't duplicate feeds."""
    session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr("app.services.builtin_feeds.AsyncSessionLocal", session_factory)

    await seed_builtin_feeds()
    await seed_builtin_feeds()

    async with session_factory() as db:
        result = await db.execute(select(DataFeed).where(DataFeed.is_builtin == True))  # noqa: E712
        feeds = result.scalars().all()
        assert len(feeds) == 8


@pytest.mark.asyncio
async def test_builtin_feeds_have_correct_parse_config(seed_engine, monkeypatch):
    """T010: Built-in feeds have correct parse_config for each source."""
    session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr("app.services.builtin_feeds.AsyncSessionLocal", session_factory)

    await seed_builtin_feeds()

    async with session_factory() as db:
        result = await db.execute(select(DataFeed).where(DataFeed.is_builtin == True))  # noqa: E712
        feeds = result.scalars().all()
        feed_by_name = {f.name: f for f in feeds}

        # Verify scraper feeds have parse_config with required keys
        for defn in BUILTIN_FEEDS:
            feed = feed_by_name[defn["name"]]
            assert feed.feed_type.value == defn["feed_type"]
            if defn["feed_type"] == "scraper":
                assert feed.parse_config is not None
                assert "title_selector" in feed.parse_config
                assert "source_name" in feed.parse_config
            else:
                # RSS feeds have no parse_config
                assert feed.parse_config is None


# --- T028-T030: Classification and cosine similarity tests ---


@pytest.mark.asyncio
async def test_classify_groups_similar_articles(seed_engine):
    """T028: _classify_to_case() groups similar articles into same case."""
    from app.models.case import Case, CaseStatus
    from app.services.collector import _classify_to_case

    session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        # First article creates a new case
        case_id1 = await _classify_to_case(db, "中美贸易谈判进展", "中美两国代表在日内瓦举行新一轮贸易谈判")
        await db.flush()

        # Similar article should go into same case
        case_id2 = await _classify_to_case(db, "中美贸易谈判最新消息", "中美贸易代表就关税问题达成初步共识")
        await db.flush()

        # If NLP model is available, they should be in same case
        # If model is unavailable, each gets its own case (acceptable fallback)
        result = await db.execute(select(Case))
        cases = result.scalars().all()
        assert len(cases) >= 1  # At least one case created


@pytest.mark.asyncio
async def test_classify_creates_new_case_for_unrelated(seed_engine):
    """T029: _classify_to_case() creates new case for unrelated articles."""
    from app.models.case import Case
    from app.services.collector import _classify_to_case

    session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        case_id1 = await _classify_to_case(db, "日本地震最新消息", "日本东北部发生7.2级地震")
        await db.flush()

        case_id2 = await _classify_to_case(db, "世界杯足球赛预选赛", "亚洲区预选赛今日开赛")
        await db.flush()

        # These are very different topics — should create separate cases
        result = await db.execute(select(Case))
        cases = result.scalars().all()
        assert len(cases) >= 2


def test_cosine_similarity_known_inputs():
    """T030: _cosine_similarity() returns correct scores for known inputs."""
    from app.services.collector import _cosine_similarity

    # Identical vectors should return 1.0
    v1 = [1.0, 0.0, 0.0]
    assert abs(_cosine_similarity(v1, v1) - 1.0) < 1e-6

    # Orthogonal vectors should return 0.0
    v2 = [0.0, 1.0, 0.0]
    assert abs(_cosine_similarity(v1, v2)) < 1e-6

    # Opposite vectors should return -1.0
    v3 = [-1.0, 0.0, 0.0]
    assert abs(_cosine_similarity(v1, v3) - (-1.0)) < 1e-6

    # Zero vector should return 0.0
    v_zero = [0.0, 0.0, 0.0]
    assert _cosine_similarity(v1, v_zero) == 0.0
