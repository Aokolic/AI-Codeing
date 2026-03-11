"""Contract tests — Tags endpoints (FR-010)."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tags_empty(client: AsyncClient):
    resp = await client.get("/api/v1/tags")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient):
    resp = await client.post(
        "/api/v1/tags",
        json={"id": "", "name": "医疗"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "医疗"


@pytest.mark.asyncio
async def test_create_duplicate_tag_rejected(client: AsyncClient):
    await client.post("/api/v1/tags", json={"id": "", "name": "政治"})
    resp = await client.post("/api/v1/tags", json={"id": "", "name": "政治"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_tag_case_count(client: AsyncClient):
    tag_resp = await client.post(
        "/api/v1/tags", json={"id": "", "name": "经济"}
    )
    tag_id = tag_resp.json()["id"]

    await client.post(
        "/api/v1/cases",
        json={"title": "通货膨胀报道", "tag_ids": [tag_id]},
    )

    tags = await client.get("/api/v1/tags")
    econ = next((t for t in tags.json() if t["name"] == "经济"), None)
    assert econ is not None
    assert econ["case_count"] >= 1
