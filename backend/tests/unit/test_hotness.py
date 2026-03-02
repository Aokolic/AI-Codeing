"""Unit tests — Hotness scoring computation."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.case import CaseStatus
from app.services.hotness import compute_hotness


def test_hotness_active_case_higher_than_closed():
    now = datetime.now(timezone.utc)
    created = now - timedelta(days=5)
    active = compute_hotness(event_count=10, source_count=5, status=CaseStatus.active, created_at=created)
    closed = compute_hotness(event_count=10, source_count=5, status=CaseStatus.closed, created_at=created)
    assert active > closed


def test_hotness_zero_events():
    now = datetime.now(timezone.utc)
    score = compute_hotness(event_count=0, source_count=0, status=CaseStatus.active, created_at=now)
    assert score >= 0.0


def test_hotness_many_sources_increases_score():
    now = datetime.now(timezone.utc)
    low = compute_hotness(10, 1, CaseStatus.active, now - timedelta(days=10))
    high = compute_hotness(10, 20, CaseStatus.active, now - timedelta(days=10))
    assert high > low


def test_hotness_maximum_capped():
    now = datetime.now(timezone.utc)
    score = compute_hotness(
        event_count=1000, source_count=200, status=CaseStatus.active, created_at=now - timedelta(days=1)
    )
    assert score <= 100.0
