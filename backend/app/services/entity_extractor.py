"""Entity extraction for Chinese text using jieba word segmentation.

Provides keyword/entity extraction (person, place, organization names)
and Jaccard overlap calculation for case-level topic grouping.
"""
from __future__ import annotations

import logging

import jieba.posseg as pseg

logger = logging.getLogger(__name__)

# POS tags considered as named entities or significant nouns:
#   nr = person name, ns = place name, nt = organization,
#   nz = other proper noun, n = general noun (only if len > 1)
_ENTITY_POS_TAGS = {"nr", "ns", "nt", "nz"}
_NOUN_POS_TAG = "n"

# Common stopwords to filter out single-char or generic nouns
_STOPWORDS = frozenset(
    "的了是在有和与为被所从到对于但而"
    "也不就都又将把让由此被以及等能被"
    "个中大上下新多少全各自本该每两"
    "人们事情时候问题方面情况工作发展"
    "进行表示认为指出强调说称据报道"
)


def extract_entities(text: str) -> set[str]:
    """Extract key entities from Chinese text using jieba POS tagging.

    Returns a set of entity strings (person/place/org names + significant nouns).
    """
    if not text or not text.strip():
        return set()

    entities: set[str] = set()
    for word, flag in pseg.cut(text):
        word = word.strip()
        if not word:
            continue
        # Named entities: nr, ns, nt, nz
        if flag in _ENTITY_POS_TAGS and len(word) >= 2:
            entities.add(word)
        # General nouns longer than 1 char, not stopwords
        elif flag == _NOUN_POS_TAG and len(word) >= 2 and word not in _STOPWORDS:
            entities.add(word)

    return entities


def entity_overlap(a: set[str], b: set[str]) -> float:
    """Compute Jaccard similarity between two entity sets.

    Returns len(a & b) / len(a | b), or 0.0 if both sets are empty.
    """
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)
