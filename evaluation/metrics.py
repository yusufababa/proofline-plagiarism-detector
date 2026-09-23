from __future__ import annotations


def binary_metrics(labels: list[int], predictions: list[int]) -> dict[str, float | int]:
    """Calculate dependency-free binary classification metrics."""

    if len(labels) != len(predictions):
        raise ValueError("Labels and predictions must have the same length.")
    if not labels:
        raise ValueError("At least one labelled example is required.")

    tp = sum(label == 1 and prediction == 1 for label, prediction in zip(labels, predictions))
    tn = sum(label == 0 and prediction == 0 for label, prediction in zip(labels, predictions))
    fp = sum(label == 0 and prediction == 1 for label, prediction in zip(labels, predictions))
    fn = sum(label == 1 and prediction == 0 for label, prediction in zip(labels, predictions))

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(labels)
    false_positive_rate = fp / (fp + tn) if fp + tn else 0.0

    return {
        "examples": len(labels),
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "false_positive_rate": round(false_positive_rate, 4),
    }


def predictions_at_threshold(scores: list[float], threshold: float) -> list[int]:
    return [int(score >= threshold) for score in scores]


def select_threshold(scores: list[float], labels: list[int]) -> tuple[float, dict[str, float | int]]:
    """Choose a threshold on validation data only, prioritising F1 then precision."""

    if len(scores) != len(labels):
        raise ValueError("Scores and labels must have the same length.")
    if not scores:
        raise ValueError("Validation data is required to select a threshold.")

    best_threshold = 0.5
    best_metrics = binary_metrics(labels, predictions_at_threshold(scores, best_threshold))
    best_key = (
        float(best_metrics["f1"]),
        float(best_metrics["precision"]),
        float(best_metrics["recall"]),
        best_threshold,
    )

    for step in range(5, 101, 5):
        threshold = step / 100
        metrics = binary_metrics(labels, predictions_at_threshold(scores, threshold))
        key = (
            float(metrics["f1"]),
            float(metrics["precision"]),
            float(metrics["recall"]),
            threshold,
        )
        if key > best_key:
            best_threshold = threshold
            best_metrics = metrics
            best_key = key

    return best_threshold, best_metrics

