"""Unit tests — Credibility scoring engine."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from app.models.credibility import CredibilityLevel
from app.models.source import SourceType
from app.services.credibility import compute_credibility


def _make_source(name: str, stype: SourceType, has_false_history: bool = False) -> MagicMock:
    s = MagicMock()
    s.id = name
    s.name = name
    s.source_type = stype
    s.has_false_history = has_false_history
    s.reputation_score = 80.0
    s.url = "http://example.com"
    s.collected_at = datetime.now(timezone.utc)
    return s


def test_no_sources_returns_unverified():
    result = compute_credibility([], datetime.now(timezone.utc))
    assert result["level"] == CredibilityLevel.unverified
    assert result["total_score"] == 0.0


def test_government_source_high_authority():
    sources = [_make_source("官方机构", SourceType.government)]
    result = compute_credibility(sources, datetime.now(timezone.utc))
    assert result["authority_score"] >= 75.0


def test_false_history_reduces_authority():
    clean = _make_source("可信媒体", SourceType.government)
    dirty = _make_source("低信媒体", SourceType.government, has_false_history=True)
    r_clean = compute_credibility([clean], datetime.now(timezone.utc))
    r_dirty = compute_credibility([dirty], datetime.now(timezone.utc))
    assert r_clean["authority_score"] > r_dirty["authority_score"]


def test_conflict_detection_two_high_authority():
    s1 = _make_source("新华社", SourceType.government)
    s2 = _make_source("人民日报", SourceType.mainstream_media)
    result = compute_credibility([s1, s2], datetime.now(timezone.utc))
    assert result["has_conflict"] is True
    assert len(result["conflict_sources"]) == 2


def test_timeliness_decays_with_age():
    recent = datetime.now(timezone.utc)
    old = datetime.now(timezone.utc) - timedelta(days=30)
    src = [_make_source("媒体", SourceType.mainstream_media)]
    r_recent = compute_credibility(src, recent)
    r_old = compute_credibility(src, old)
    assert r_recent["timeliness_score"] > r_old["timeliness_score"]


def test_cross_verify_increases_with_source_count():
    sources_1 = [_make_source(f"来源{i}", SourceType.local_media) for i in range(1)]
    sources_4 = [_make_source(f"来源{i}", SourceType.local_media) for i in range(4)]
    t = datetime.now(timezone.utc)
    assert compute_credibility(sources_4, t)["cross_verify_score"] > compute_credibility(sources_1, t)["cross_verify_score"]
