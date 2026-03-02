"""Unit tests — Case lifecycle transition logic."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.case import Case, CaseStatus
from app.services.case_lifecycle import run_lifecycle_transitions, transition_case_on_new_event

TEST_DB = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(TEST_DB, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_active_to_observing(session: AsyncSession):
    case = Case(
        id=str(uuid.uuid4()),
        title="Test",
        status=CaseStatus.active,
        created_at=datetime.now(timezone.utc) - timedelta(days=35),
        last_event_at=datetime.now(timezone.utc) - timedelta(days=35),
    )
    session.add(case)
    await session.commit()

    await run_lifecycle_transitions(session)
    await session.commit()
    await session.refresh(case)
    assert case.status == CaseStatus.observing


@pytest.mark.asyncio
async def test_observing_to_closed(session: AsyncSession):
    case = Case(
        id=str(uuid.uuid4()),
        title="Test",
        status=CaseStatus.observing,
        created_at=datetime.now(timezone.utc) - timedelta(days=95),
        last_event_at=datetime.now(timezone.utc) - timedelta(days=95),
    )
    session.add(case)
    await session.commit()

    await run_lifecycle_transitions(session)
    await session.commit()
    await session.refresh(case)
    assert case.status == CaseStatus.closed


@pytest.mark.asyncio
async def test_new_event_restores_active(session: AsyncSession):
    case = Case(
        id=str(uuid.uuid4()),
        title="Test",
        status=CaseStatus.observing,
        created_at=datetime.now(timezone.utc) - timedelta(days=60),
    )
    session.add(case)
    await session.commit()

    await transition_case_on_new_event(session, case.id)
    await session.refresh(case)
    assert case.status == CaseStatus.active
