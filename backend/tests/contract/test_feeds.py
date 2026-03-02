"""Contract tests — DataFeed CRUD + collection trigger endpoints."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_feed_requires_auth(client: AsyncClient):
    resp = await client.post(
        "/api/v1/feeds",
        json={"name": "Test RSS", "url": "https://example.com/rss", "feed_type": "rss"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_and_list_feeds(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/feeds",
        json={"name": "新华社RSS", "url": "https://xinhuanet.com/rss.xml", "feed_type": "rss"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "新华社RSS"
    assert data["feed_type"] == "rss"
    feed_id = data["id"]

    list_resp = await client.get("/api/v1/feeds", headers=auth_headers)
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert body["total"] >= 1
    ids = [f["id"] for f in body["items"]]
    assert feed_id in ids


@pytest.mark.asyncio
async def test_update_feed(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/feeds",
        json={"name": "Old Name", "url": "https://example.com/rss", "feed_type": "rss"},
        headers=auth_headers,
    )
    feed_id = create.json()["id"]

    patch = await client.patch(
        f"/api/v1/feeds/{feed_id}",
        json={"name": "New Name"},
        headers=auth_headers,
    )
    assert patch.status_code == 200
    assert patch.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_feed(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/feeds",
        json={"name": "Deletable", "url": "https://example.com/rss", "feed_type": "rss"},
        headers=auth_headers,
    )
    feed_id = create.json()["id"]
    del_resp = await client.delete(f"/api/v1/feeds/{feed_id}", headers=auth_headers)
    assert del_resp.status_code == 204
