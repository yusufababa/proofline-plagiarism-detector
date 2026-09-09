from __future__ import annotations

import math


class HybridSimilarityModel:
    """Explainable weighted baseline to compare with learned fusion later."""

    name = "hybrid"

    def __init__(self, lexical_weight: float, semantic_weight: float) -> None:
        if not math.isclose(lexical_weight + semantic_weight, 1.0):
            raise ValueError("Hybrid weights must sum to 1.0.")
        self.lexical_weight = lexical_weight
        self.semantic_weight = semantic_weight

    def score(self, lexical: float, semantic: float | None) -> float:
        if semantic is None:
            return lexical
        combined = (self.lexical_weight * lexical) + (self.semantic_weight * semantic)
        return round(combined, 4)


def review_band(score: float) -> str:
    """Provisional bands that Objective 3 will replace with calibrated values."""

    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "medium"
    return "low"

