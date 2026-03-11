"""Built-in media feed definitions and seed function.

Provides 8 international Chinese-language RSS sources that are
pre-configured on first startup so users can browse news with zero configuration.
"""
from __future__ import annotations

import logging

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.data_feed import DataFeed, FeedType

logger = logging.getLogger(__name__)

BUILTIN_FEEDS: list[dict] = [
    {
        "name": "BBC中文",
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "德国之声中文",
        "url": "https://rss.dw.com/xml/rss-chi-all",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "法广RFI中文",
        "url": "https://www.rfi.fr/cn/rss",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "纽约时报中文",
        "url": "https://cn.nytimes.com/rss/",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "韩联社中文",
        "url": "https://cn.yna.co.kr/RSS/news.xml",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "NHK中文",
        "url": "https://www3.nhk.or.jp/nhkworld/zh/news/list.json",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "联合早报",
        "url": "https://www.zaobao.com/rss",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "CNA中央通讯社",
        "url": "https://www.cna.com.tw/rss/aall.xml",
        "feed_type": "rss",
        "parse_config": None,
    },
]


async def seed_builtin_feeds() -> None:
    """Insert missing built-in feeds on startup (idempotent)."""
    async with AsyncSessionLocal() as db:
        inserted = 0
        for feed_def in BUILTIN_FEEDS:
            existing = await db.execute(
                select(DataFeed).where(
                    DataFeed.url == feed_def["url"],
                    DataFeed.is_builtin == True,  # noqa: E712
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue

            feed = DataFeed(
                name=feed_def["name"],
                url=feed_def["url"],
                feed_type=FeedType[feed_def["feed_type"]],
                parse_config=feed_def["parse_config"],
                is_builtin=True,
                schedule_cron="*/30 * * * *",
            )
            db.add(feed)
            inserted += 1

        await db.commit()
        if inserted:
            logger.info("Seeded %d built-in feeds.", inserted)
        else:
            logger.info("All built-in feeds already present.")
