"""Contract tests — Search endpoint (FR-011)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_empty_query_rejected(client: AsyncClient):
    resp = await client.get("/api/v1/cases/search?q=")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_returns_list(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/cases",
        json={"title": "某某明星离婚事件"},
        headers=auth_headers,
    )
    resp = await client.get("/api/v1/cases/search?q=离婚")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_search_limit_respected(client: AsyncClient, auth_headers: dict):
    for i in range(5):
        await client.post(
            "/api/v1/cases",
            json={"title": f"经济数据造假案例{i}"},
            headers=auth_headers,
        )
    resp = await client.get("/api/v1/cases/search?q=经济&limit=3")
    assert resp.status_code == 200
    assert len(resp.json()) <= 3
