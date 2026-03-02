"""Auto case lifecycle transitions (FR-013).

Rules:
  active  → observing : 30 days without new EventNode
  observing → closed  : 90 days without new EventNode
  any → active        : new EventNode added
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseStatus

logger = logging.getLogger(__name__)

ACTIVE_TO_OBSERVING_DAYS = 30
OBSERVING_TO_CLOSED_DAYS = 90


async def transition_case_on_new_event(db: AsyncSession, case_id: str) -> None:
    """Called when a new EventNode is added: restore status to active."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case and case.status != CaseStatus.active:
        old = case.status
        case.status = CaseStatus.active
        case.last_event_at = datetime.now(timezone.utc)
        await db.flush()
        logger.info("Case %s: %s → active (new event)", case_id, old)


async def run_lifecycle_transitions(db: AsyncSession) -> None:
    """Batch job: scan all non-closed cases and apply time-based transitions."""
    now = datetime.now(timezone.utc)
    observing_threshold = now - timedelta(days=ACTIVE_TO_OBSERVING_DAYS)
    closed_threshold = now - timedelta(days=OBSERVING_TO_CLOSED_DAYS)

    result = await db.execute(
        select(Case).where(Case.status != CaseStatus.closed)
    )
    cases = result.scalars().all()

    for case in cases:
        ref_time = case.last_event_at or case.created_at
        if ref_time.tzinfo is None:
            ref_time = ref_time.replace(tzinfo=timezone.utc)

        if case.status == CaseStatus.active and ref_time < observing_threshold:
            case.status = CaseStatus.observing
            logger.info("Case %s: active → observing (30d idle)", case.id)
        elif case.status == CaseStatus.observing and ref_time < closed_threshold:
            case.status = CaseStatus.closed
            logger.info("Case %s: observing → closed (90d idle)", case.id)

    await db.flush()
