"""Events API endpoints (FR-005 — timeline display, FR-007 — event detail)."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.case import Case
from app.models.credibility import CredibilityAssessment
from app.models.event_node import EventNode
from app.models.source import EventNodeSource, Source
from app.schemas.event_node import CredibilityBrief, EventDetail, EventSummary, SourceBrief

router = APIRouter(tags=["events"])


@router.get("/cases/{case_id}/events", response_model=list[EventSummary])
async def list_events(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
):
    """Return chronological event timeline for a case with optional time range filter."""
    # Verify case exists
    case_check = await db.execute(select(Case).where(Case.id == case_id))
    if case_check.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Case not found")

    conditions = [EventNode.case_id == case_id]
    if from_time:
        conditions.append(EventNode.event_time >= from_time)
    if to_time:
        conditions.append(EventNode.event_time <= to_time)

    stmt = (
        select(EventNode)
        .where(*conditions)
        .order_by(EventNode.event_time.asc())
        .options(selectinload(EventNode.event_sources).selectinload(EventNodeSource.source))
    )
    nodes = (await db.execute(stmt)).scalars().all()

    results = []
    for node in nodes:
        # Fetch credibility brief
        cred_result = await db.execute(
            select(CredibilityAssessment)
            .where(CredibilityAssessment.event_node_id == node.id)
            .order_by(CredibilityAssessment.assessed_at.desc())
            .limit(1)
        )
        cred = cred_result.scalar_one_or_none()

        cred_brief = None
        if cred:
            cred_brief = CredibilityBrief(
                level=cred.level,
                total_score=cred.total_score,
                has_conflict=cred.has_conflict,
            )

        source_briefs = [
            SourceBrief(
                id=es.source.id,
                name=es.source.name,
                source_type=es.source.source_type,
                url=es.source.url,
                reputation_score=es.source.reputation_score,
                has_false_history=es.source.has_false_history,
                collected_at=es.source.collected_at,
            )
            for es in node.event_sources
        ]

        results.append(
            EventSummary(
                id=node.id,
                title=node.title,
                event_time=node.event_time,
                source_count=len(source_briefs),
                credibility=cred_brief,
                sources=source_briefs,
            )
        )
    return results


@router.get("/events/{event_id}", response_model=EventDetail)
async def get_event(
    event_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Get full event node detail including all associated sources."""
    result = await db.execute(select(EventNode).where(EventNode.id == event_id))
    node = result.scalar_one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Sources
    src_result = await db.execute(
        select(Source)
        .join(EventNodeSource, EventNodeSource.source_id == Source.id)
        .where(EventNodeSource.event_node_id == event_id)
    )
    sources = [
        SourceBrief(
            id=s.id,
            name=s.name,
            source_type=s.source_type,
            url=s.url,
            reputation_score=s.reputation_score,
            has_false_history=s.has_false_history,
            collected_at=s.collected_at,
        )
        for s in src_result.scalars().all()
    ]

    # Latest credibility assessment
    cred_result = await db.execute(
        select(CredibilityAssessment)
        .where(CredibilityAssessment.event_node_id == event_id)
        .order_by(CredibilityAssessment.assessed_at.desc())
        .limit(1)
    )
    cred = cred_result.scalar_one_or_none()
    cred_brief = None
    if cred:
        cred_brief = CredibilityBrief(
            level=cred.level, total_score=cred.total_score, has_conflict=cred.has_conflict
        )

    return EventDetail(
        id=node.id,
        case_id=node.case_id,
        title=node.title,
        summary=node.summary,
        event_time=node.event_time,
        sources=sources,
        credibility=cred_brief,
    )
