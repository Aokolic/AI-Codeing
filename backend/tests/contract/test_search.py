"""Contract tests — Search endpoint (FR-011)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_empty_query_rejected(client: AsyncClient):
    resp = await client.get("/api/v1/cases/search?q=")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_returns_list(client: AsyncClient):
    await client.post(
        "/api/v1/cases",
        json={"title": "某某明星离婚事件"},
    )
    resp = await client.get("/api/v1/cases/search?q=离婚")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    item = data[0]
    # Now returns CaseSummary with full fields
    assert "title" in item
    assert "hotness_score" in item
    assert "tags" in item
    assert "event_count" in item
    assert "source_count" in item


@pytest.mark.asyncio
async def test_search_limit_respected(client: AsyncClient):
    for i in range(5):
        await client.post(
            "/api/v1/cases",
            json={"title": f"经济数据造假案例{i}"},
        )
    resp = await client.get("/api/v1/cases/search?q=经济&limit=3")
    assert resp.status_code == 200
    assert len(resp.json()) <= 3
