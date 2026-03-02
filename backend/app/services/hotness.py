"""Hotness scoring service (FR-012).

Formula (multi-dimensional weighted):
  hotness = (update_freq_score * 0.4) + (source_score * 0.3) + (status_score * 0.3)
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseStatus
from app.models.event_node import EventNode
from app.models.source import EventNodeSource

logger = logging.getLogger(__name__)

# Status weight mapping
STATUS_WEIGHTS = {CaseStatus.active: 1.0, CaseStatus.observing: 0.5, CaseStatus.closed: 0.1}


def _update_frequency_score(event_count: int, days_since_first: float) -> float:
    """Score based on events-per-day rate, capped at 100."""
    if days_since_first <= 0:
        return 50.0
    rate = event_count / days_since_first
    return min(100.0, rate * 20.0)


def _source_score(source_count: int) -> float:
    return min(100.0, source_count * 10.0)


def _status_score(status: CaseStatus) -> float:
    return STATUS_WEIGHTS.get(status, 0.1) * 100.0


def compute_hotness(
    event_count: int,
    source_count: int,
    status: CaseStatus,
    created_at: datetime,
) -> float:
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    days = max(1.0, (now - created_at).total_seconds() / 86400)

    freq = _update_frequency_score(event_count, days)
    src = _source_score(source_count)
    st = _status_score(status)

    return round(freq * 0.4 + src * 0.3 + st * 0.3, 2)


async def refresh_hotness(db: AsyncSession, case_id: str) -> None:
    """Recalculate and persist hotness_score for a single case."""
    stmt = select(Case).where(Case.id == case_id)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    if case is None:
        return

    # Event count
    evt_count_result = await db.execute(
        select(func.count(EventNode.id)).where(EventNode.case_id == case_id)
    )
    event_count = evt_count_result.scalar_one() or 0

    # Source count (distinct sources via EventNodeSource join)
    src_count_result = await db.execute(
        select(func.count(EventNodeSource.source_id.distinct()))
        .join(EventNode, EventNode.id == EventNodeSource.event_node_id)
        .where(EventNode.case_id == case_id)
    )
    source_count = src_count_result.scalar_one() or 0

    case.hotness_score = compute_hotness(event_count, source_count, case.status, case.created_at)
    await db.flush()
    logger.debug("Updated hotness for case %s: %.2f", case_id, case.hotness_score)
