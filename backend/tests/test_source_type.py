"""Unit tests for _detect_source_type heuristic (T007)."""
from app.models.source import SourceType
from app.services.collector import _detect_source_type


def test_bbc_mainstream():
    assert _detect_source_type("BBC中文", "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml") == SourceType.mainstream_media


def test_dw_mainstream():
    assert _detect_source_type("德国之声中文", "https://rss.dw.com/xml/rss-chi-all") == SourceType.mainstream_media


def test_rfi_mainstream():
    assert _detect_source_type("法广RFI中文", "https://www.rfi.fr/cn/rss") == SourceType.mainstream_media


def test_nyt_mainstream():
    assert _detect_source_type("纽约时报中文", "https://cn.nytimes.com/rss/") == SourceType.mainstream_media


def test_yna_mainstream():
    assert _detect_source_type("韩联社中文", "https://cn.yna.co.kr/RSS/news.xml") == SourceType.mainstream_media


def test_nhk_mainstream():
    assert _detect_source_type("NHK中文", "https://www3.nhk.or.jp/nhkworld/zh/news/list.json") == SourceType.mainstream_media


def test_zaobao_mainstream():
    assert _detect_source_type("联合早报", "https://www.zaobao.com/rss") == SourceType.mainstream_media


def test_cna_mainstream():
    assert _detect_source_type("CNA中央通讯社", "https://www.cna.com.tw/rss/aall.xml") == SourceType.mainstream_media


def test_government_detection():
    assert _detect_source_type("国务院新闻办", "https://gov.cn") == SourceType.government


def test_social_media_detection():
    assert _detect_source_type("微博热搜", "https://weibo.com") == SourceType.social_media


def test_unknown_falls_to_local():
    assert _detect_source_type("某地方报纸", "https://example.com") == SourceType.local_media
