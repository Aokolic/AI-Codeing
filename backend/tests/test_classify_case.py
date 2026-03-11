"""Unit tests for enhanced _classify_to_case two-layer logic (T012)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.models.case import Case, CaseStatus


@pytest.fixture
def mock_cases():
    """Create mock Case objects for testing."""
    case1 = MagicMock(spec=Case)
    case1.id = "case-iran"
    case1.title = "伊朗局势持续紧张"
    case1.status = CaseStatus.active

    case2 = MagicMock(spec=Case)
    case2.id = "case-tech"
    case2.title = "科技公司季度财报发布"
    case2.status = CaseStatus.active

    return [case1, case2]


@pytest.fixture
def mock_db(mock_cases):
    """Create a mock async db session that returns our cases."""
    db = AsyncMock()
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = mock_cases
    db.execute = AsyncMock(return_value=result_mock)
    db.flush = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.mark.asyncio
async def test_classify_groups_related_articles_by_entity(mock_db, mock_cases):
    """Articles about the same topic (Iran) should group via entity overlap."""
    with patch("app.services.collector.encode_text", return_value=None), \
         patch("app.services.collector.extract_entities") as mock_extract:
        # Article about Iran → shares entity "伊朗" with case-iran
        mock_extract.side_effect = lambda t: (
            {"伊朗", "停战"} if "停战" in t else
            {"伊朗", "局势"} if "伊朗" in t else
            {"科技", "财报"} if "科技" in t else set()
        )

        from app.services.collector import _classify_to_case
        case_id = await _classify_to_case(mock_db, "伊朗停战谈判最新进展", "相关报道...")

        # Should match case-iran via entity overlap (伊朗 shared)
        assert case_id == "case-iran"


@pytest.mark.asyncio
async def test_classify_separates_unrelated_articles(mock_db, mock_cases):
    """Unrelated articles should create a new case."""
    with patch("app.services.collector.encode_text", return_value=None), \
         patch("app.services.collector.extract_entities") as mock_extract, \
         patch("app.services.collector._create_case_from_article", new_callable=AsyncMock) as mock_create:
        # Article about sports — no entity overlap with iran or tech cases
        mock_extract.side_effect = lambda t: (
            {"伊朗", "局势"} if "伊朗" in t else
            {"科技", "财报"} if "科技" in t else
            {"足球", "世界杯"} if "足球" in t else set()
        )
        mock_create.return_value = "case-new"

        from app.services.collector import _classify_to_case
        case_id = await _classify_to_case(mock_db, "足球世界杯预选赛开幕", "比赛报道...")

        assert case_id == "case-new"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_classify_uses_semantic_when_available(mock_db, mock_cases):
    """When semantic model is available, high cosine should match."""
    with patch("app.services.collector.encode_text") as mock_encode, \
         patch("app.services.collector.extract_entities", return_value=set()), \
         patch("app.services.collector._cosine_similarity") as mock_cos:
        # Simulate semantic model available
        mock_encode.return_value = [0.1] * 768
        # High semantic score for case-iran
        mock_cos.side_effect = lambda a, b: 0.6  # > 0.45 threshold

        from app.services.collector import _classify_to_case
        case_id = await _classify_to_case(mock_db, "中东冲突升级", "相关报道...")

        # Should match via semantic alone (0.6 >= 0.45)
        assert case_id == "case-iran"


@pytest.mark.asyncio
async def test_classify_combined_entity_and_semantic(mock_db, mock_cases):
    """Combined: entity overlap >= 0.3 AND semantic >= 0.35 should match."""
    with patch("app.services.collector.encode_text") as mock_encode, \
         patch("app.services.collector.extract_entities") as mock_extract, \
         patch("app.services.collector._cosine_similarity") as mock_cos:
        mock_encode.return_value = [0.1] * 768
        # Moderate entity overlap with Iran case
        mock_extract.side_effect = lambda t: (
            {"伊朗", "局势"} if "伊朗" in t else
            {"科技", "财报"} if "科技" in t else
            {"伊朗", "航运"} if "航运" in t else set()
        )
        # Moderate semantic similarity (< 0.45 alone, but combined with entity should match)
        mock_cos.return_value = 0.38

        from app.services.collector import _classify_to_case
        case_id = await _classify_to_case(mock_db, "伊朗航运成本大幅上升", "")

        # overlap({"伊朗","航运"}, {"伊朗","局势"}) = 1/3 ≈ 0.33 >= 0.3
        # semantic 0.38 >= 0.35 → match!
        assert case_id == "case-iran"
