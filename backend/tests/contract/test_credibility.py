"""Contract tests — Credibility assessment endpoint (FR-003, FR-008, FR-017)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseStatus
from app.models.event_node import EventNode
from app.models.source import EventNodeSource, Source, SourceType


async def _seed_event_with_sources(db: AsyncSession) -> str:
    case_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())
    db.add(Case(id=case_id, title="TC", status=CaseStatus.active, created_at=datetime.now(timezone.utc)))
    db.add(EventNode(id=event_id, case_id=case_id, title="事件", summary="摘要", event_time=datetime.now(timezone.utc)))
    for name, stype in [("新华社", SourceType.mainstream_media), ("人民日报", SourceType.government)]:
        src_id = str(uuid.uuid4())
        db.add(Source(id=src_id, name=name, source_type=stype, url="https://example.com", reputation_score=80.0, collected_at=datetime.now(timezone.utc)))
        db.add(EventNodeSource(event_node_id=event_id, source_id=src_id))
    await db.commit()
    return event_id


@pytest.mark.asyncio
async def test_get_credibility(client: AsyncClient, db_session: AsyncSession):
    event_id = await _seed_event_with_sources(db_session)
    resp = await client.get(f"/api/v1/events/{event_id}/credibility")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_score" in body
    assert body["total_score"] > 0
    assert "level" in body
    assert "detail" in body


@pytest.mark.asyncio
async def test_credibility_event_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/events/nonexistent/credibility")
    assert resp.status_code == 404
