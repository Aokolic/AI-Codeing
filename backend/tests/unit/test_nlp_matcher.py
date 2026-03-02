"""Unit tests — NLP semantic matcher."""
from __future__ import annotations

import pytest

from app.services.nlp_matcher import cosine_similarity, encode_text


def test_cosine_similarity_identical():
    v = [1.0, 0.0, 0.0]
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    assert cosine_similarity(a, b) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)


def test_encode_text_returns_list_or_none():
    """encode_text should return list[float] or None (if model not available)."""
    result = encode_text("测试文本")
    assert result is None or isinstance(result, list)


def test_encode_text_vector_length():
    """If model loaded successfully, vector length should be 768."""
    result = encode_text("新冠疫苗副作用数据造假")
    if result is not None:
        assert len(result) == 768
