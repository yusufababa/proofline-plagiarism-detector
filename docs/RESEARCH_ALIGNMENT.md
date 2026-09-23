# Research Alignment

## Objective 1

Design and implement document preprocessing together with lexical and semantic similarity algorithms.

Implementation evidence:

- `document_extractor.py` for supported academic-document formats.
- `preprocessing.py` for normalization and passage segmentation.
- `lexical.py` for direct and lightly disguised overlap.
- `semantic.py` for paraphrase-oriented similarity.
- Tests showing deterministic preprocessing and lexical behaviour.

## Objective 2

Integrate lexical and semantic evidence into an explainable decision-support model.

Implementation evidence:

- `scanner.py` coordinates both algorithms.
- `hybrid.py` defines an explicit, reviewable baseline formula.
- The API exposes component scores instead of only one unexplained percentage.
- The dashboard displays matched passages and their source document.
- `calibration.py` derives evidence-priority bands using validation categories only.
- `CALIBRATION_RESULTS.md` documents the deployed pilot thresholds and untouched test check.

Pilot evidence now available:

- Thirty synthetic labelled passage pairs covering direct copy, light editing, paraphrase, cited quotation, and unrelated text.
- Source-grouped train, validation, and untouched test splits.
- A generated feature table containing word, character, and lexical scores.
- Citation and quotation exclusions evaluated separately from raw textual similarity.
- Logistic-regression fusion trained on the training split and compared with the weighted baseline.

The pilot calibration must be repeated on the larger independently reviewed dataset before final effectiveness claims are made.

## Objective 3

Evaluate the system with recognized quantitative metrics.

Required experimental outputs:

- One untouched test split.
- Lexical-only, semantic-only, and hybrid predictions.
- Precision, recall, F1-score, false-positive rate, and processing time.
- Error analysis divided into direct copy, light modification, paraphrase, legitimate quotation, bibliography, and unrelated topical similarity.
- Ablation results for word, character, and semantic signals.

The v0.4.0 pilot runner already calculates the required classification metrics, selects thresholds only on validation data, reports runtime and traced Python memory, and exports per-case features. Its small synthetic dataset validates the method but is not sufficient for final effectiveness claims.

The application progress percentage is an engineering tracker. It is not an evaluation result and must not be presented as model accuracy.
