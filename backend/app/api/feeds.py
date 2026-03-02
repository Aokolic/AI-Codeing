"""Data feeds API endpoints — full CRUD + manual collection trigger (JWT-protected)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import require_auth
from app.database import get_session
from app.models.data_feed import DataFeed, FeedStatus
from app.schemas.common import PaginatedResponse
from app.schemas.data_feed import CollectTriggerResponse, DataFeedCreate, DataFeedOut, DataFeedUpdate
from app.services.audit import log_action
from app.services.collector import run_collection_for_feed

router = APIRouter(prefix="/feeds", tags=["feeds"])


@router.get("", response_model=PaginatedResponse[DataFeedOut])
async def list_feeds(
    db: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(require_auth)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    total = (await db.execute(select(func.count(DataFeed.id)))).scalar_one() or 0
    stmt = (
        select(DataFeed)
        .order_by(DataFeed.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = (await db.execute(stmt)).scalars().all()
    items = [DataFeedOut.model_validate(f) for f in rows]
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=DataFeedOut, status_code=status.HTTP_201_CREATED)
async def create_feed(
    body: DataFeedCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(require_auth)],
):
    feed = DataFeed(
        id=str(uuid.uuid4()),
        name=body.name,
        url=str(body.url),
        feed_type=body.feed_type,
        schedule_cron=body.schedule_cron or "0 2 * * *",
        parse_config=body.parse_config,
        status=FeedStatus.normal,
        consecutive_failures=0,
        created_at=datetime.now(timezone.utc),
    )
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    log_action(actor, "CREATE", "DataFeed", feed.id)
    return DataFeedOut.model_validate(feed)


@router.patch("/{feed_id}", response_model=DataFeedOut)
async def update_feed(
    feed_id: str,
    body: DataFeedUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(require_auth)],
):
    result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
    feed = result.scalar_one_or_none()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    if body.name is not None:
        feed.name = body.name
    if body.url is not None:
        feed.url = str(body.url)
    if body.schedule_cron is not None:
        feed.schedule_cron = body.schedule_cron
    if body.status is not None:
        feed.status = body.status
    if body.parse_config is not None:
        feed.parse_config = body.parse_config

    await db.commit()
    await db.refresh(feed)
    log_action(actor, "UPDATE", "DataFeed", feed_id)
    return DataFeedOut.model_validate(feed)


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed(
    feed_id: str,
    db: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(require_auth)],
):
    result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
    feed = result.scalar_one_or_none()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    await db.delete(feed)
    await db.commit()
    log_action(actor, "DELETE", "DataFeed", feed_id)


@router.post("/{feed_id}/collect", response_model=CollectTriggerResponse)
async def trigger_collect(
    feed_id: str,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_session)],
    actor: Annotated[str, Depends(require_auth)],
):
    """Manually trigger data collection for a specific feed (runs in background)."""
    result = await db.execute(select(DataFeed).where(DataFeed.id == feed_id))
    feed = result.scalar_one_or_none()
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    background_tasks.add_task(run_collection_for_feed, feed_id)
    log_action(actor, "TRIGGER_COLLECT", "DataFeed", feed_id)
    return CollectTriggerResponse(
        feed_id=feed_id,
        message=f"Collection started for feed '{feed.name}'",
        triggered_at=datetime.now(timezone.utc),
    )
