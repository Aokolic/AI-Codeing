"""Tags API endpoints (FR-010 — tag management)."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import require_auth
from app.database import get_session
from app.models.case import CaseTag, Tag
from app.schemas.case import TagOut, TagWithCount

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagWithCount])
async def list_tags(
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """Return all tags with their case usage counts."""
    stmt = (
        select(Tag, func.count(CaseTag.case_id).label("case_count"))
        .outerjoin(CaseTag, CaseTag.tag_id == Tag.id)
        .group_by(Tag.id)
        .order_by(func.count(CaseTag.case_id).desc())
    )
    rows = (await db.execute(stmt)).all()
    return [TagWithCount(id=tag.id, name=tag.name, case_count=count) for tag, count in rows]


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(
    body: TagOut,
    db: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(require_auth)],
):
    """Create a new tag. Returns existing tag if name already exists (idempotent)."""
    existing = (
        await db.execute(select(Tag).where(Tag.name == body.name))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag '{body.name}' already exists",
        )

    tag = Tag(id=str(uuid.uuid4()), name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return TagOut(id=tag.id, name=tag.name)
