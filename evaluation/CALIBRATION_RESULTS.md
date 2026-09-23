# Proofline Review-Band Calibration

Version 0.10.0 replaces the hand-set review bands with a reproducible pilot calibration. The bands describe similarity-evidence priority; they do not state that misconduct occurred.

## Method

Only the labelled validation split was used to select thresholds. The test split was not inspected during selection.

For each model, validation scores were grouped as paraphrase, light edit, and direct copy. Boundaries were placed at the midpoint between adjacent non-overlapping score ranges:

```text
medium boundary = midpoint(maximum paraphrase, minimum light edit)
high boundary   = midpoint(maximum light edit, minimum direct copy)
```

Scores below the medium boundary are low priority, scores from the medium boundary to below the high boundary are medium priority, and scores at or above the high boundary are high priority. Citation-aware quotation exclusions continue to override the band and are marked `excluded`.

## Deployed pilot thresholds

| Mode | Detection floor | Medium boundary | High boundary |
|---|---:|---:|---:|
| Lexical | 0.15 | 0.25 | 0.69 |
| Weighted hybrid | 0.20 | 0.46 | 0.80 |

The detection floor decides whether a match is shown. The band boundaries prioritize matches that passed that floor.

## Untouched pilot test check

| Mode | Precision | Recall | F1 | False-positive rate |
|---|---:|---:|---:|---:|
| Lexical | 1.0000 | 0.6667 | 0.8000 | 0.0000 |
| Weighted hybrid | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

These results come from only ten synthetic test examples. They validate the calibration procedure and software integration, not real-world accuracy. All thresholds must be recalibrated on the larger independently reviewed research dataset before the final dissertation claims are made.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner --semantic
```

Machine-readable deployed values are stored in `evaluation/calibrated_review_bands.json`.
