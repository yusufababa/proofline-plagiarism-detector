# Pilot Category and Error Analysis

Version 0.7.0 adds per-category evaluation and dissertation-ready SVG charts for all four models.

## Test category accuracy

| Category | Lexical | Semantic | Weighted hybrid | Learned fusion |
|---|---:|---:|---:|---:|
| Cited quotation | 1.00 | 1.00 | 1.00 | 1.00 |
| Direct copy | 1.00 | 1.00 | 1.00 | 1.00 |
| Light edit | 1.00 | 1.00 | 1.00 | 1.00 |
| Paraphrase | 0.00 | 0.50 | 1.00 | 1.00 |
| Unrelated | 1.00 | 1.00 | 1.00 | 1.00 |

The lexical model's two test errors were both paraphrases. MiniLM recovered one of those two cases. The fixed weighted hybrid and learned fusion recovered both. No model produced a false positive on the two unrelated pilot cases, and citation/quotation exclusions handled both legitimate quotations correctly.

These category counts are extremely small. They show that the error-analysis pipeline works, but they do not establish real-world category performance.

## Generated figures

- `evaluation/results/test_model_f1.svg` compares untouched test F1 across models.
- `evaluation/results/test_category_accuracy.svg` shows accuracy by case category and model.

The figures are generated from the JSON experiment result by `evaluation/charts.py`, avoiding manual chart transcription.

## External dataset decision

PAN-PC-11 was selected as the final external benchmark candidate. Its research-use conditions, size, DOI, and laptop-safe 600-case subset protocol are documented in `evaluation/DATASET_PLAN.md` and `evaluation/dataset_manifest.json`.

