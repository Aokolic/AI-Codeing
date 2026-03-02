"""Contract tests — Event timeline and event detail endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseStatus
from app.models.event_node import EventNode


async def _seed_case_with_event(db: AsyncSession) -> tuple[str, str]:
    case_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())
    db.add(
        Case(
            id=case_id,
            title="种子案例",
            status=CaseStatus.active,
            created_at=datetime.now(timezone.utc),
        )
    )
    db.add(
        EventNode(
            id=event_id,
            case_id=case_id,
            title="初步报道",
            summary="首次公开报道内容",
            event_time=datetime.now(timezone.utc),
        )
    )
    await db.commit()
    return case_id, event_id


@pytest.mark.asyncio
async def test_list_events_for_case(client: AsyncClient, db_session: AsyncSession):
    case_id, _ = await _seed_case_with_event(db_session)
    resp = await client.get(f"/api/v1/cases/{case_id}/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 1
    assert events[0]["title"] == "初步报道"


@pytest.mark.asyncio
async def test_get_event_detail(client: AsyncClient, db_session: AsyncSession):
    _, event_id = await _seed_case_with_event(db_session)
    resp = await client.get(f"/api/v1/events/{event_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == event_id


@pytest.mark.asyncio
async def test_events_case_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/cases/nonexistent-id/events")
    assert resp.status_code == 404
