"""Unit tests — RSS/HTML data collector helpers (no network calls)."""
from __future__ import annotations

from app.services.collector import _detect_source_type, _parse_rss
from app.models.source import SourceType


def test_detect_source_type_government():
    assert _detect_source_type("国务院官方公告", "http://gov.cn") == SourceType.government


def test_detect_source_type_mainstream():
    assert _detect_source_type("新华社", "http://xinhuanet.com") == SourceType.mainstream_media


def test_detect_source_type_social():
    assert _detect_source_type("微博热搜", "http://weibo.com") == SourceType.social_media


def test_detect_source_type_unknown():
    result = _detect_source_type("随机博客", "http://randomsite.xyz")
    assert isinstance(result, SourceType)


def test_parse_rss_valid():
    rss_content = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>新华社</title>
    <item>
      <title>重要新闻</title>
      <description>新闻摘要内容</description>
      <link>https://xinhua.com/article/1</link>
      <pubDate>Mon, 01 Jan 2024 00:00:00 +0000</pubDate>
    </item>
  </channel>
</rss>"""
    articles = _parse_rss(rss_content, "https://xinhua.com/rss")
    assert len(articles) == 1
    assert articles[0]["title"] == "重要新闻"
    assert "摘要" in articles[0]["summary"]


def test_parse_rss_empty_feed():
    rss_content = '<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>'
    articles = _parse_rss(rss_content, "https://example.com")
    assert articles == []
