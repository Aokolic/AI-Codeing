"""Unit tests for entity_extractor module (T011)."""
from app.services.entity_extractor import entity_overlap, extract_entities


def test_extract_entities_place_names():
    entities = extract_entities("伊朗总统访问北京讨论石油合作")
    # Should find place names like 伊朗, 北京
    assert "伊朗" in entities
    assert "北京" in entities


def test_extract_entities_person_names():
    entities = extract_entities("特朗普与拜登就中东问题展开辩论")
    assert "特朗普" in entities or "拜登" in entities or "中东" in entities


def test_extract_entities_organization():
    entities = extract_entities("联合国安理会讨论朝鲜半岛局势")
    # jieba extracts compound nouns like "联合国安理会", "朝鲜半岛"
    assert len(entities) > 0
    found = entities & {"联合国安理会", "朝鲜半岛", "联合国", "安理会", "朝鲜", "半岛", "局势"}
    assert len(found) >= 1


def test_extract_entities_empty_string():
    assert extract_entities("") == set()
    assert extract_entities("   ") == set()


def test_extract_entities_short_text():
    entities = extract_entities("美国")
    assert "美国" in entities


def test_entity_overlap_identical():
    a = {"伊朗", "北京", "石油"}
    assert entity_overlap(a, a) == 1.0


def test_entity_overlap_disjoint():
    a = {"伊朗", "北京"}
    b = {"巴西", "东京"}
    assert entity_overlap(a, b) == 0.0


def test_entity_overlap_partial():
    a = {"伊朗", "北京", "石油"}
    b = {"伊朗", "华盛顿", "外交"}
    # intersection = {"伊朗"}, union = {"伊朗", "北京", "石油", "华盛顿", "外交"}
    assert abs(entity_overlap(a, b) - 1 / 5) < 0.01


def test_entity_overlap_both_empty():
    assert entity_overlap(set(), set()) == 0.0


def test_entity_overlap_one_empty():
    a = {"伊朗"}
    assert entity_overlap(a, set()) == 0.0
    assert entity_overlap(set(), a) == 0.0
