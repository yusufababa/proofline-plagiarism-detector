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

Still required:

- Labelled training and validation examples.
- Comparison with logistic-regression fusion.
- Empirical threshold calibration.
- Quotation, citation, bibliography, and boilerplate handling.

## Objective 3

Evaluate the system with recognized quantitative metrics.

Required experimental outputs:

- One untouched test split.
- Lexical-only, semantic-only, and hybrid predictions.
- Precision, recall, F1-score, false-positive rate, and processing time.
- Error analysis divided into direct copy, light modification, paraphrase, legitimate quotation, bibliography, and unrelated topical similarity.
- Ablation results for word, character, and semantic signals.

The application progress percentage is an engineering tracker. It is not an evaluation result and must not be presented as model accuracy.

