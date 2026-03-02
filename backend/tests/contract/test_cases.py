"""Contract tests — Cases list, create, update, search endpoints."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_cases_empty(client: AsyncClient):
    resp = await client.get("/api/v1/cases")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


@pytest.mark.asyncio
async def test_create_case_requires_auth(client: AsyncClient):
    resp = await client.post("/api/v1/cases", json={"title": "Test"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_and_get_case(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/cases",
        json={"title": "COVID-19疫苗争议", "description": "关于疫苗副作用的不实信息"},
        headers=auth_headers,
    )
    assert create.status_code == 201
    case_id = create.json()["id"]
    assert create.json()["title"] == "COVID-19疫苗争议"

    get = await client.get(f"/api/v1/cases/{case_id}")
    assert get.status_code == 200
    assert get.json()["id"] == case_id


@pytest.mark.asyncio
async def test_update_case_title(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/cases",
        json={"title": "原始标题"},
        headers=auth_headers,
    )
    case_id = create.json()["id"]
    patch = await client.patch(
        f"/api/v1/cases/{case_id}",
        json={"title": "更新后的标题"},
        headers=auth_headers,
    )
    assert patch.status_code == 200
    assert patch.json()["title"] == "更新后的标题"


@pytest.mark.asyncio
async def test_search_cases(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/cases",
        json={"title": "新冠病毒溯源报告"},
        headers=auth_headers,
    )
    search = await client.get("/api/v1/cases/search?q=新冠")
    assert search.status_code == 200
    results = search.json()
    assert isinstance(results, list)
    assert any("新冠" in r["title"] for r in results)
