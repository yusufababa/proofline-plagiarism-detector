from __future__ import annotations

import math
from collections import Counter

from app.domain import LexicalScore
from app.services.preprocessing import tokenize


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    common = left.keys() & right.keys()
    numerator = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _character_ngrams(text: str, size: int = 4) -> set[str]:
    compact = " ".join(tokenize(text))
    if not compact:
        return set()
    if len(compact) <= size:
        return {compact}
    return {compact[index:index + size] for index in range(len(compact) - size + 1)}


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


class LexicalSimilarityModel:
    """Low-memory lexical baseline with separately reported component scores."""

    name = "lexical"

    def score(self, left: str, right: str) -> LexicalScore:
        word_score = _cosine(Counter(tokenize(left)), Counter(tokenize(right)))
        character_score = _jaccard(_character_ngrams(left), _character_ngrams(right))
        combined = (0.70 * word_score) + (0.30 * character_score)
        return LexicalScore(
            word_cosine=round(word_score, 4),
            character_jaccard=round(character_score, 4),
            combined=round(combined, 4),
        )

