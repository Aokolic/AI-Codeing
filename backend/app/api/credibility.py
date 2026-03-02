"""Credibility assessment API endpoint (FR-003, FR-008, FR-009a, FR-017)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.credibility import CredibilityAssessment
from app.models.event_node import EventNode
from app.models.source import EventNodeSource, Source
from app.schemas.credibility import CredibilityDetail, CredibilityOverall, ScoringExplanation, SourceWithCredibility
from app.services.credibility import compute_credibility

router = APIRouter(tags=["credibility"])


@router.get("/events/{event_id}/credibility", response_model=CredibilityOverall)
async def get_credibility(
    event_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Return full credibility assessment for an event node (compute on-the-fly and cache)."""
    node_result = await db.execute(select(EventNode).where(EventNode.id == event_id))
    node = node_result.scalar_one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Load associated sources
    src_result = await db.execute(
        select(Source)
        .join(EventNodeSource, EventNodeSource.source_id == Source.id)
        .where(EventNodeSource.event_node_id == event_id)
    )
    sources = src_result.scalars().all()

    # Compute credibility
    result = compute_credibility(list(sources), node.event_time)

    # Persist/update cached assessment
    existing_cred = (
        await db.execute(
            select(CredibilityAssessment)
            .where(CredibilityAssessment.event_node_id == event_id)
            .limit(1)
        )
    ).scalar_one_or_none()

    if existing_cred is None:
        existing_cred = CredibilityAssessment(
            id=str(uuid.uuid4()),
            event_node_id=event_id,
        )
        db.add(existing_cred)

    existing_cred.level = result["level"]
    existing_cred.total_score = result["total_score"]
    existing_cred.authority_score = result["authority_score"]
    existing_cred.timeliness_score = result["timeliness_score"]
    existing_cred.cross_verify_score = result["cross_verify_score"]
    existing_cred.source_count = result["source_count"]
    existing_cred.has_conflict = result["has_conflict"]
    existing_cred.conflict_sources_json = json.dumps(result["conflict_sources"])
    existing_cred.assessed_at = datetime.now(timezone.utc)
    await db.commit()

    # Build response
    source_items = [
        SourceWithCredibility(
            source_id=s["source_id"],
            source_name=s["source_name"],
            source_type=s["source_type"],
            url=s["url"],
            reputation_score=s["reputation_score"],
            has_false_history=s["has_false_history"],
            authority_contribution=s["authority_contribution"],
            is_accessible=s["is_accessible"],
            collected_at=s["collected_at"],
            warnings=s["warnings"],
        )
        for s in result["source_details"]
    ]

    exp = result.get("scoring_explanation", {})
    scoring_exp = ScoringExplanation(
        authority=exp.get("authority", ""),
        timeliness=exp.get("timeliness", ""),
        cross_verify=exp.get("cross_verify", ""),
    )

    detail = CredibilityDetail(
        event_id=event_id,
        event_title=node.title,
        level=result["level"],
        total_score=result["total_score"],
        authority_score=result["authority_score"],
        timeliness_score=result["timeliness_score"],
        cross_verify_score=result["cross_verify_score"],
        source_count=result["source_count"],
        has_conflict=result["has_conflict"],
        conflict_sources=result["conflict_sources"],
        sources=source_items,
        scoring_explanation=scoring_exp,
        assessed_at=existing_cred.assessed_at,
    )

    return CredibilityOverall(
        event_id=event_id,
        level=result["level"],
        total_score=result["total_score"],
        has_conflict=result["has_conflict"],
        conflict_sources=result["conflict_sources"],
        detail=detail,
    )
