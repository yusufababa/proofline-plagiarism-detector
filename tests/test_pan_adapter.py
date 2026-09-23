import tempfile
import unittest
from pathlib import Path

from evaluation.pan_adapter import (
    PanCase,
    assign_source_group_splits,
    export_manifest,
    load_pan_cases,
    select_stratified_cases,
)


class PanAdapterTests(unittest.TestCase):
    def test_loads_offsets_languages_and_obfuscation_categories(self):
        fixture = Path(__file__).parent / "fixtures" / "pan_sample"
        cases = load_pan_cases(fixture)

        self.assertEqual(len(cases), 2)
        self.assertEqual({case.category for case in cases}, {"direct_copy", "paraphrase"})
        direct = next(case for case in cases if case.category == "direct_copy")
        self.assertEqual(
            direct.candidate_text,
            "Renewable energy systems reduce emissions and improve energy security.",
        )
        self.assertEqual(direct.candidate_text, direct.source_text)

    def test_source_groups_never_cross_splits(self):
        cases = [
            PanCase(
                str(index),
                f"s{index}",
                f"source{index // 2}",
                0,
                1,
                0,
                1,
                "a",
                "b",
                "direct_copy",
            )
            for index in range(10)
        ]
        assign_source_group_splits(cases)
        splits_by_source: dict[str, set[str]] = {}
        for case in cases:
            splits_by_source.setdefault(case.source_reference, set()).add(case.split)
        self.assertTrue(all(len(splits) == 1 for splits in splits_by_source.values()))
        self.assertEqual({case.split for case in cases}, {"train", "validation", "test"})

    def test_exports_machine_readable_manifest(self):
        fixture = Path(__file__).parent / "fixtures" / "pan_sample"
        cases = load_pan_cases(fixture)
        assign_source_group_splits(cases)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "manifest.json"
            export_manifest(cases, output, fixture)
            content = output.read_text(encoding="utf-8")
        self.assertIn('"dataset": "PAN-PC-11"', content)
        self.assertIn('"cases": 2', content)

    def test_limited_selection_is_category_balanced(self):
        cases = [
            PanCase(
                f"{category}-{index}",
                f"s-{category}-{index}",
                f"source-{category}-{index}",
                0,
                1,
                0,
                1,
                "a",
                "b",
                category,
            )
            for category in ("direct_copy", "light_edit", "paraphrase")
            for index in range(5)
        ]
        selected = select_stratified_cases(cases, 9)
        counts = {
            category: sum(case.category == category for case in selected)
            for category in {case.category for case in selected}
        }
        self.assertEqual(set(counts.values()), {3})


if __name__ == "__main__":
    unittest.main()
