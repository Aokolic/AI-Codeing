"""Cases API endpoints (FR-006, FR-010, FR-011, FR-012, FR-013)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.database import get_session
from app.models.case import Case, CaseStatus, CaseTag, Tag
from app.models.event_node import EventNode
from app.models.source import EventNodeSource
from app.schemas.case import (
    CaseCreate,
    CaseDetail,
    CaseSummary,
    CaseUpdate,
    SearchSuggestedCase,
    TagOut,
)
from app.schemas.common import PaginatedResponse
from app.services.audit import log_action
from app.services.hotness import refresh_hotness

router = APIRouter(prefix="/cases", tags=["cases"])
settings = get_settings()


async def _case_summary(db: AsyncSession, case: Case) -> CaseSummary:
    """Build CaseSummary with computed counts and tags."""
    evt_count = (
        await db.execute(
            select(func.count(EventNode.id)).where(EventNode.case_id == case.id)
        )
    ).scalar_one() or 0

    src_count = (
        await db.execute(
            select(func.count(EventNodeSource.source_id.distinct()))
            .join(EventNode, EventNode.id == EventNodeSource.event_node_id)
            .where(EventNode.case_id == case.id)
        )
    ).scalar_one() or 0

    tag_result = await db.execute(
        select(Tag)
        .join(CaseTag, CaseTag.tag_id == Tag.id)
        .where(CaseTag.case_id == case.id)
    )
    tags = [TagOut(id=t.id, name=t.name) for t in tag_result.scalars().all()]

    return CaseSummary(
        id=case.id,
        title=case.title,
        status=case.status,
        hotness_score=case.hotness_score,
        event_count=evt_count,
        source_count=src_count,
        tags=tags,
        created_at=case.created_at,
        last_event_at=case.last_event_at,
    )


@router.get("", response_model=PaginatedResponse[CaseSummary])
async def list_cases(
    db: Annotated[AsyncSession, Depends(get_session)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: CaseStatus | None = None,
    tag_id: str | None = None,
    sort: str = Query("hotness", pattern="^(hotness|created_at)$"),
):
    """List cases sorted by hotness (default) or creation date."""
    conditions = []
    if status is not None:
        conditions.append(Case.status == status)
    if tag_id:
        sub = select(CaseTag.case_id).where(CaseTag.tag_id == tag_id)
        conditions.append(Case.id.in_(sub))

    order_col = Case.hotness_score.desc() if sort == "hotness" else Case.created_at.desc()

    total_result = await db.execute(
        select(func.count(Case.id)).where(and_(*conditions) if conditions else True)
    )
    total = total_result.scalar_one() or 0

    stmt = (
        select(Case)
        .where(and_(*conditions) if conditions else True)
        .order_by(order_col)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(stmt)).scalars().all()
    items = [await _case_summary(db, c) for c in rows]

    return PaginatedResponse(
        total=total, page=page, page_size=page_size, items=items
    )


@router.get("/search", response_model=list[CaseSummary])
async def search_cases(
    db: Annotated[AsyncSession, Depends(get_session)],
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(10, ge=1, le=50),
):
    """Full-text search using ts_vector (PostgreSQL) or ILIKE (SQLite fallback)."""
    if settings.is_sqlite:
        # SQLite fallback: ILIKE-style via LIKE
        pattern = f"%{q}%"
        stmt = (
            select(Case)
            .where(or_(Case.title.like(pattern), Case.description.like(pattern)))
            .limit(limit)
        )
    else:
        # PostgreSQL: use to_tsvector / to_tsquery
        from sqlalchemy import text as sa_text

        stmt = (
            select(Case)
            .where(
                sa_text(
                    "to_tsvector('jiebaqry', title || ' ' || coalesce(description,'')) @@ plainto_tsquery('jiebaqry', :q)"
                ).bindparams(q=q)
            )
            .limit(limit)
        )

    rows = (await db.execute(stmt)).scalars().all()
    return [await _case_summary(db, c) for c in rows]


@router.get("/{case_id}", response_model=CaseDetail)
async def get_case(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    summary = await _case_summary(db, case)
    return CaseDetail(
        **summary.model_dump(),
        description=case.description,
    )


@router.post("", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
async def create_case(
    body: CaseCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    case = Case(
        id=str(uuid.uuid4()),
        title=body.title,
        description=body.description,
        status=CaseStatus.active,
        created_at=datetime.now(timezone.utc),
    )
    db.add(case)
    await db.flush()

    for tag_id in body.tag_ids or []:
        db.add(CaseTag(case_id=case.id, tag_id=tag_id))

    await db.commit()
    log_action("system", "CREATE", "Case", case.id)
    return await get_case(case.id, db)


@router.patch("/{case_id}", response_model=CaseDetail)
async def update_case(
    case_id: str,
    body: CaseUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    if body.title is not None:
        case.title = body.title
    if body.description is not None:
        case.description = body.description
    if body.status is not None:
        case.status = body.status

    if body.tag_ids is not None:
        from sqlalchemy import delete as sa_delete
        await db.execute(
            sa_delete(CaseTag).where(CaseTag.case_id == case_id)
        )
        for tag_id in body.tag_ids:
            db.add(CaseTag(case_id=case_id, tag_id=tag_id))

    await refresh_hotness(db, case_id)
    await db.commit()
    log_action("system", "UPDATE", "Case", case_id)
    return await get_case(case_id, db)
