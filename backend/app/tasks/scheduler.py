"""APScheduler task scheduler — runs cron jobs for data collection and lifecycle transitions."""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.data_feed import DataFeed, FeedStatus
from app.services.case_lifecycle import run_lifecycle_transitions
from app.services.collector import run_collection_for_feed

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _collect_all_active_feeds() -> None:
    """Collect all non-offline feeds."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(DataFeed).where(DataFeed.status != FeedStatus.offline)
        )
        feeds = result.scalars().all()
        feed_ids = [f.id for f in feeds]

    for fid in feed_ids:
        try:
            await run_collection_for_feed(fid)
        except Exception as exc:
            logger.error("Error collecting feed %s: %s", fid, exc)


async def _run_lifecycle() -> None:
    """Run case lifecycle transitions."""
    async with AsyncSessionLocal() as db:
        try:
            await run_lifecycle_transitions(db)
            await db.commit()
        except Exception as exc:
            logger.error("Lifecycle transition error: %s", exc)


def start_scheduler() -> None:
    """Initialize and start the APScheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = AsyncIOScheduler()

    # Default: collect all feeds every 2 hours
    _scheduler.add_job(
        _collect_all_active_feeds,
        CronTrigger.from_crontab("0 */2 * * *"),
        id="collect_all_feeds",
        replace_existing=True,
        misfire_grace_time=300,
    )

    # Lifecycle transitions: run daily at 03:00
    _scheduler.add_job(
        _run_lifecycle,
        CronTrigger.from_crontab("0 3 * * *"),
        id="lifecycle_transitions",
        replace_existing=True,
        misfire_grace_time=300,
    )

    _scheduler.start()
    logger.info("Scheduler started with %d jobs.", len(_scheduler.get_jobs()))


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
