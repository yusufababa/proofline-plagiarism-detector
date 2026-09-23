from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from statistics import median
from typing import Any


def _category_scores(
    rows: list[dict[str, Any]], category: str, score_key: str
) -> list[float]:
    return sorted(
        float(row[score_key])
        for row in rows
        if row["category"] == category
        and int(row["review_label"]) == 1
        and not row.get("predicted_exclusion", False)
    )


def _boundary_between(lower_scores: list[float], upper_scores: list[float]) -> float:
    if not lower_scores or not upper_scores:
        raise ValueError("Every calibration category must contain labelled validation scores.")

    lower_anchor = max(lower_scores)
    upper_anchor = min(upper_scores)
    if lower_anchor >= upper_anchor:
        lower_anchor = median(lower_scores)
        upper_anchor = median(upper_scores)
    if lower_anchor >= upper_anchor:
        raise ValueError(
            "The validation score distributions are not ordered enough to calibrate bands."
        )
    midpoint = (Decimal(str(lower_anchor)) + Decimal(str(upper_anchor))) / Decimal("2")
    return float(midpoint.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calibrate_review_bands(
    validation_rows: list[dict[str, Any]], score_key: str
) -> dict[str, Any]:
    """Derive review bands from validation categories without looking at test data."""

    paraphrase_scores = _category_scores(validation_rows, "paraphrase", score_key)
    light_edit_scores = _category_scores(validation_rows, "light_edit", score_key)
    direct_copy_scores = _category_scores(validation_rows, "direct_copy", score_key)

    medium_threshold = _boundary_between(paraphrase_scores, light_edit_scores)
    high_threshold = _boundary_between(light_edit_scores, direct_copy_scores)
    if medium_threshold >= high_threshold:
        raise ValueError("Calibrated medium threshold must be below the high threshold.")

    return {
        "medium_threshold": medium_threshold,
        "high_threshold": high_threshold,
        "method": "midpoints between adjacent validation-category score ranges",
        "calibration_split": "validation",
        "test_split_used": False,
        "category_scores": {
            "paraphrase": paraphrase_scores,
            "light_edit": light_edit_scores,
            "direct_copy": direct_copy_scores,
        },
    }
