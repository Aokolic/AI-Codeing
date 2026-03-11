"""Built-in media feed definitions and seed function.

Provides 8 mainstream media sources (6 HTML scrapers + 2 RSS) that are
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
        "name": "新浪新闻",
        "url": "https://news.sina.com.cn/roll/",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": ".news-item h2 a, .list-a li a",
            "summary_selector": ".news-item .content, .list-a li .txt",
            "source_name": "新浪新闻",
        },
    },
    {
        "name": "澎湃新闻",
        "url": "https://www.thepaper.cn/",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": "a[href*='newsDetail_forward']",
            "summary_selector": ".small_cardcontent__BTALp p",
            "source_name": "澎湃新闻",
        },
    },
    {
        "name": "环球时报",
        "url": "https://www.globaltimes.cn/",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": ".row-content a .title, .lead_title a",
            "summary_selector": ".row-content .summary",
            "source_name": "环球时报",
        },
    },
    {
        "name": "央视新闻",
        "url": "https://news.cctv.com/",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": ".title a, .text h3 a",
            "summary_selector": ".text .brief, .text p",
            "source_name": "央视新闻",
        },
    },
    {
        "name": "BBC中文",
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "feed_type": "rss",
        "parse_config": None,
    },
    {
        "name": "联合早报",
        "url": "https://www.zaobao.com/realtime/china",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": ".article-title a, [href*='/story'] .title",
            "summary_selector": ".article-excerpt, .article-abstract",
            "source_name": "联合早报",
        },
    },
    {
        "name": "新华网",
        "url": "https://www.news.cn/",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": ".tit a, .domPC_listTitle a",
            "summary_selector": ".des, .domPC_listDes",
            "source_name": "新华网",
        },
    },
    {
        "name": "南方都市报",
        "url": "https://news.southcn.com/",
        "feed_type": "scraper",
        "parse_config": {
            "title_selector": ".list-item .title a, .news-list h3 a",
            "summary_selector": ".list-item .desc, .news-list .summary",
            "source_name": "南方都市报",
        },
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
