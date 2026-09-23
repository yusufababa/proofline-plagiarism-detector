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


def review_band(score: float, medium_threshold: float = 0.46, high_threshold: float = 0.80) -> str:
    """Assign validation-calibrated evidence priority without deciding misconduct."""

    if not 0 <= medium_threshold < high_threshold <= 1:
        raise ValueError("Review-band thresholds must be ordered between 0 and 1.")
    if score >= high_threshold:
        return "high"
    if score >= medium_threshold:
        return "medium"
    return "low"
