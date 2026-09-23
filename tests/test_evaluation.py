import unittest
from pathlib import Path

from evaluation.metrics import binary_metrics, predictions_at_threshold, select_threshold
from evaluation.runner import evaluate, load_examples, process_peak_memory_mb
from evaluation.charts import render_category_accuracy_chart, render_test_f1_chart
from evaluation.calibration import calibrate_review_bands


class EvaluationTests(unittest.TestCase):
    def test_binary_metrics_calculate_confusion_matrix(self):
        metrics = binary_metrics([1, 1, 0, 0], [1, 0, 1, 0])
        self.assertEqual(metrics["true_positive"], 1)
        self.assertEqual(metrics["true_negative"], 1)
        self.assertEqual(metrics["false_positive"], 1)
        self.assertEqual(metrics["false_negative"], 1)
        self.assertEqual(metrics["f1"], 0.5)

    def test_threshold_predictions_are_inclusive(self):
        self.assertEqual(predictions_at_threshold([0.49, 0.5, 0.9], 0.5), [0, 1, 1])

    def test_threshold_is_selected_from_validation_scores(self):
        threshold, metrics = select_threshold([0.9, 0.7, 0.2, 0.1], [1, 1, 0, 0])
        self.assertGreater(threshold, 0.2)
        self.assertLessEqual(threshold, 0.7)
        self.assertEqual(metrics["f1"], 1.0)

    def test_review_bands_are_calibrated_from_validation_categories(self):
        rows = [
            {"category": "paraphrase", "review_label": 1, "score": 0.23},
            {"category": "paraphrase", "review_label": 1, "score": 0.37},
            {"category": "light_edit", "review_label": 1, "score": 0.55},
            {"category": "light_edit", "review_label": 1, "score": 0.59},
            {"category": "direct_copy", "review_label": 1, "score": 1.0},
        ]

        bands = calibrate_review_bands(rows, "score")

        self.assertEqual(bands["medium_threshold"], 0.46)
        self.assertEqual(bands["high_threshold"], 0.8)
        self.assertEqual(bands["calibration_split"], "validation")
        self.assertFalse(bands["test_split_used"])

    def test_pilot_dataset_has_leakage_safe_splits(self):
        dataset_path = Path(__file__).resolve().parents[1] / "evaluation" / "pilot_dataset.json"
        _, examples = load_examples(dataset_path)
        source_splits: dict[str, set[str]] = {}
        for example in examples:
            source_splits.setdefault(example["source_id"], set()).add(example["split"])
        self.assertTrue(all(len(splits) == 1 for splits in source_splits.values()))
        self.assertEqual({row["split"] for row in examples}, {"train", "validation", "test"})
        self.assertEqual(len(examples), 30)

    def test_lexical_pilot_evaluates_untouched_test_split(self):
        dataset_path = Path(__file__).resolve().parents[1] / "evaluation" / "pilot_dataset.json"
        result = evaluate(dataset_path)
        lexical = result["models"]["lexical"]
        test_review = lexical["splits"]["test"]["end_to_end_review"]
        self.assertEqual(result["experiment"]["examples"], 30)
        valid_thresholds = [step / 100 for step in range(5, 101, 5)]
        self.assertIn(lexical["threshold_selected_on_validation"], valid_thresholds)
        self.assertEqual(test_review["false_positive"], 0)
        self.assertGreater(test_review["f1"], 0)
        self.assertEqual(
            lexical["review_bands_selected_on_validation"]["medium_threshold"], 0.25
        )
        self.assertEqual(
            lexical["review_bands_selected_on_validation"]["high_threshold"], 0.69
        )

    def test_process_memory_measurement_is_positive_when_supported(self):
        peak_memory = process_peak_memory_mb()
        self.assertTrue(peak_memory is None or peak_memory > 0)

    def test_evaluation_includes_category_analysis_and_svg_charts(self):
        dataset_path = Path(__file__).resolve().parents[1] / "evaluation" / "pilot_dataset.json"
        result = evaluate(dataset_path)
        lexical = result["models"]["lexical"]
        self.assertEqual(len(lexical["test_category_analysis"]), 5)
        self.assertIn("<svg", render_test_f1_chart(result))
        self.assertIn("Test Accuracy by Case Category", render_category_accuracy_chart(result))


if __name__ == "__main__":
    unittest.main()
