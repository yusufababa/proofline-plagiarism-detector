from __future__ import annotations

import argparse
import ctypes
import json
import os
import time
import tracemalloc
from collections import Counter
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.models import (
    HybridSimilarityModel,
    LexicalSimilarityModel,
    LogisticRegressionFusionModel,
    SemanticSimilarityModel,
)
from app.services.preprocessing import contains_citation, is_quotation
from evaluation.calibration import calibrate_review_bands
from evaluation.charts import write_charts
from evaluation.metrics import binary_metrics, predictions_at_threshold, select_threshold


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "evaluation" / "pilot_dataset.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports"
FUSION_FEATURE_NAMES = ["word_cosine", "character_jaccard", "semantic_score"]


def process_peak_memory_mb() -> float | None:
    """Return peak resident process memory, including native model allocations."""

    if os.name == "nt":
        from ctypes import wintypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        get_memory_info = ctypes.windll.kernel32.K32GetProcessMemoryInfo
        get_memory_info.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        get_memory_info.restype = wintypes.BOOL
        success = get_memory_info(
            ctypes.windll.kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        )
        return round(counters.PeakWorkingSetSize / (1024 * 1024), 2) if success else None

    try:
        import resource

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        divisor = 1024 if peak > 1024 * 1024 else 1
        return round(peak / divisor, 2)
    except (ImportError, OSError):
        return None


def load_examples(dataset_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    examples: list[dict[str, Any]] = []
    source_splits: dict[str, str] = {}

    for source in dataset.get("sources", []):
        source_id = source["source_id"]
        split = source["split"]
        if split not in {"train", "validation", "test"}:
            raise ValueError(f"Unsupported split '{split}' for source '{source_id}'.")
        if source_id in source_splits and source_splits[source_id] != split:
            raise ValueError(f"Source leakage detected for '{source_id}'.")
        source_splits[source_id] = split

        for case in source.get("cases", []):
            examples.append(
                {
                    "case_id": case["case_id"],
                    "source_id": source_id,
                    "source_title": source["title"],
                    "split": split,
                    "category": case["category"],
                    "source_text": source["source_text"],
                    "candidate_text": case["candidate_text"],
                    "similarity_label": int(case["similarity_label"]),
                    "review_label": int(case["review_label"]),
                }
            )

    if not examples:
        raise ValueError("The evaluation dataset contains no cases.")
    if not {"train", "validation", "test"}.issubset({row["split"] for row in examples}):
        raise ValueError("The dataset must contain train, validation, and test splits.")
    return dataset, examples


def _evaluate_split(rows: list[dict[str, Any]], score_key: str, threshold: float) -> dict[str, Any]:
    review_scores = [0.0 if row["predicted_exclusion"] else row[score_key] for row in rows]
    review_labels = [row["review_label"] for row in rows]
    similarity_scores = [row[score_key] for row in rows]
    similarity_labels = [row["similarity_label"] for row in rows]
    return {
        "examples": len(rows),
        "similarity_detection": binary_metrics(
            similarity_labels,
            predictions_at_threshold(similarity_scores, threshold),
        ),
        "end_to_end_review": binary_metrics(
            review_labels,
            predictions_at_threshold(review_scores, threshold),
        ),
    }


def _category_analysis(
    rows: list[dict[str, Any]], score_key: str, threshold: float
) -> dict[str, Any]:
    analysis: dict[str, Any] = {}
    for category in sorted({row["category"] for row in rows}):
        category_rows = [row for row in rows if row["category"] == category]
        review_scores = [
            0.0 if row["predicted_exclusion"] else row[score_key] for row in category_rows
        ]
        predictions = predictions_at_threshold(review_scores, threshold)
        labels = [row["review_label"] for row in category_rows]
        errors = [
            {
                "case_id": row["case_id"],
                "expected": label,
                "predicted": prediction,
                "score": round(score, 4),
            }
            for row, label, prediction, score in zip(
                category_rows, labels, predictions, review_scores, strict=True
            )
            if label != prediction
        ]
        correct = len(category_rows) - len(errors)
        analysis[category] = {
            "examples": len(category_rows),
            "correct": correct,
            "incorrect": len(errors),
            "accuracy": round(correct / len(category_rows), 4),
            "mean_review_score": round(sum(review_scores) / len(review_scores), 4),
            "errors": errors,
        }
    return analysis


def evaluate(dataset_path: Path, include_semantic: bool = False) -> dict[str, Any]:
    dataset, examples = load_examples(dataset_path)
    lexical_model = LexicalSimilarityModel()
    semantic_model = SemanticSimilarityModel(
        settings.semantic_model_name,
        cache_folder=settings.semantic_cache_dir,
    )
    hybrid_model = HybridSimilarityModel(settings.lexical_weight, settings.semantic_weight)

    if include_semantic and not semantic_model.available:
        raise RuntimeError(
            "Semantic evaluation was requested, but sentence-transformers is not installed. "
            "Run: pip install -r requirements-semantic.txt"
        )

    tracemalloc.start()
    started = time.perf_counter()
    for row in examples:
        lexical = lexical_model.score(row["candidate_text"], row["source_text"])
        row["word_cosine"] = lexical.word_cosine
        row["character_jaccard"] = lexical.character_jaccard
        row["lexical_score"] = lexical.combined
        row["quotation_detected"] = is_quotation(row["candidate_text"])
        row["citation_detected"] = contains_citation(row["candidate_text"])
        row["predicted_exclusion"] = row["quotation_detected"] and row["citation_detected"]

    model_score_keys = {"lexical": "lexical_score"}
    dependency_versions: dict[str, str] = {}
    learned_parameters: dict[str, object] | None = None
    if include_semantic:
        import sentence_transformers
        import torch
        import transformers

        dependency_versions = {
            "sentence_transformers": sentence_transformers.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        }
        pairs = [(row["candidate_text"], row["source_text"]) for row in examples]
        semantic_scores = semantic_model.score_many(pairs)
        for row, semantic_score in zip(examples, semantic_scores, strict=True):
            row["semantic_score"] = semantic_score
            row["hybrid_score"] = hybrid_model.score(row["lexical_score"], semantic_score)
        training_rows = [row for row in examples if row["split"] == "train"]
        learned_model = LogisticRegressionFusionModel()
        learned_model.fit(
            [[row[name] for name in FUSION_FEATURE_NAMES] for row in training_rows],
            [row["similarity_label"] for row in training_rows],
        )
        for row in examples:
            row["learned_fusion_score"] = learned_model.score(
                [row[name] for name in FUSION_FEATURE_NAMES]
            )
        learned_parameters = learned_model.parameters(FUSION_FEATURE_NAMES)
        model_score_keys.update(
            {
                "semantic": "semantic_score",
                "hybrid": "hybrid_score",
                "learned_fusion": "learned_fusion_score",
            }
        )

    elapsed_seconds = time.perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    model_results: dict[str, Any] = {}
    for model_name, score_key in model_score_keys.items():
        validation = [row for row in examples if row["split"] == "validation"]
        validation_scores = [
            0.0 if row["predicted_exclusion"] else row[score_key] for row in validation
        ]
        validation_labels = [row["review_label"] for row in validation]
        threshold, calibration_metrics = select_threshold(validation_scores, validation_labels)
        review_bands = calibrate_review_bands(validation, score_key)
        model_result = {
            "threshold_selected_on_validation": threshold,
            "validation_calibration": calibration_metrics,
            "review_bands_selected_on_validation": review_bands,
            "splits": {
                split: _evaluate_split(
                    [row for row in examples if row["split"] == split],
                    score_key,
                    threshold,
                )
                for split in ("train", "validation", "test")
            },
            "test_category_analysis": _category_analysis(
                [row for row in examples if row["split"] == "test"],
                score_key,
                threshold,
            ),
        }
        if model_name == "learned_fusion":
            model_result["training"] = {
                "split": "train",
                "target": "similarity_label",
                "examples": sum(row["split"] == "train" for row in examples),
                "parameters": learned_parameters,
            }
        model_results[model_name] = model_result

    return {
        "experiment": {
            "dataset_name": dataset["name"],
            "dataset_version": dataset["version"],
            "dataset_license": dataset["license"],
            "dataset_notice": dataset["description"],
            "examples": len(examples),
            "source_groups": len(dataset["sources"]),
            "split_counts": dict(Counter(row["split"] for row in examples)),
            "category_counts": dict(Counter(row["category"] for row in examples)),
            "semantic_requested": include_semantic,
            "semantic_model": settings.semantic_model_name if include_semantic else None,
            "dependency_versions": dependency_versions,
            "elapsed_seconds": round(elapsed_seconds, 4),
            "python_peak_memory_mb": round(peak_bytes / (1024 * 1024), 4),
            "process_peak_memory_mb": process_peak_memory_mb(),
        },
        "models": model_results,
        "features": examples,
    }


def render_markdown(result: dict[str, Any]) -> str:
    experiment = result["experiment"]
    lines = [
        "# Proofline Pilot Evaluation Results",
        "",
        "> This synthetic pilot validates the experiment pipeline. It is not the final research dataset.",
        "",
        f"- Dataset: {experiment['dataset_name']} v{experiment['dataset_version']}",
        f"- Licence: {experiment['dataset_license']}",
        f"- Examples: {experiment['examples']} across {experiment['source_groups']} source groups",
        f"- Split counts: {experiment['split_counts']}",
        f"- Runtime: {experiment['elapsed_seconds']} seconds",
        f"- Traced Python peak memory: {experiment['python_peak_memory_mb']} MB",
        f"- Process peak memory: {experiment['process_peak_memory_mb']} MB",
        f"- Dependency versions: {experiment['dependency_versions'] or 'base lexical install'}",
        "",
    ]

    for model_name, model in result["models"].items():
        lines.extend(
            [
                f"## {model_name.replace('_', ' ').title()} model",
                "",
                f"Validation-selected threshold: `{model['threshold_selected_on_validation']:.2f}`",
                f"Review bands: low below `{model['review_bands_selected_on_validation']['medium_threshold']:.2f}`, "
                f"medium from that boundary to below `{model['review_bands_selected_on_validation']['high_threshold']:.2f}`, "
                "and high at or above the high boundary.",
                "",
                "| Split | Task | Precision | Recall | F1 | Accuracy | FPR | TP | TN | FP | FN |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for split, split_result in model["splits"].items():
            for task_name, label in (
                ("similarity_detection", "Similarity"),
                ("end_to_end_review", "Review after exclusions"),
            ):
                metrics = split_result[task_name]
                lines.append(
                    f"| {split.title()} | {label} | {metrics['precision']:.4f} | "
                    f"{metrics['recall']:.4f} | {metrics['f1']:.4f} | "
                    f"{metrics['accuracy']:.4f} | {metrics['false_positive_rate']:.4f} | "
                    f"{metrics['true_positive']} | {metrics['true_negative']} | "
                    f"{metrics['false_positive']} | {metrics['false_negative']} |"
                )
        lines.append("")
        if "training" in model:
            parameters = model["training"]["parameters"]
            lines.extend(
                [
                    f"Training split: `{model['training']['split']}` only; "
                    f"{model['training']['examples']} examples.",
                    f"Features: `{parameters['feature_names']}`",
                    f"Standardized coefficients: `{parameters['coefficients']}`; "
                    f"intercept: `{parameters['intercept']}`",
                    "",
                ]
            )
        lines.extend(
            [
                "### Test category analysis",
                "",
                "| Category | Examples | Correct | Incorrect | Accuracy | Mean review score |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for category, category_result in model["test_category_analysis"].items():
            lines.append(
                f"| {_label_for_report(category)} | {category_result['examples']} | "
                f"{category_result['correct']} | {category_result['incorrect']} | "
                f"{category_result['accuracy']:.4f} | "
                f"{category_result['mean_review_score']:.4f} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- Thresholds were selected using validation data only.",
            "- Review-band boundaries were placed between validation paraphrase, light-edit, and direct-copy score ranges.",
            "- Test data was not used during threshold selection.",
            "- Similarity metrics measure textual relationship, including correctly cited quotations.",
            "- Review metrics apply the citation-and-quotation exclusion before classification.",
            "- Paraphrase misses are expected in the lexical baseline and motivate the MiniLM comparison.",
            "- Learned fusion is fitted on training data only; validation selects its threshold.",
            "",
        ]
    )
    return "\n".join(lines)


def _label_for_report(value: str) -> str:
    return value.replace("_", " ").title()


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Proofline models on labelled passage pairs.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Also evaluate MiniLM semantic and weighted-hybrid models.",
    )
    args = parser.parse_args()

    result = evaluate(args.dataset, include_semantic=args.semantic)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "evaluation_results.json"
    markdown_path = args.output_dir / "evaluation_results.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(result), encoding="utf-8")
    chart_paths = write_charts(result, args.output_dir)
    print(f"Evaluation complete: {json_path}")
    print(f"Readable report: {markdown_path}")
    print("Charts: " + ", ".join(str(path) for path in chart_paths))


if __name__ == "__main__":
    main()
