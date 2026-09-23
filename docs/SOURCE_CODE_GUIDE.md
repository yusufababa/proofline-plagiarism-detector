# Source Code Guide

## Root files

| File | Responsibility |
|---|---|
| `.env` | Active local settings; not committed to version control |
| `.env.example` | Safe configuration template |
| `pyproject.toml` | Project metadata and development-tool settings |
| `requirements.txt` | Lightweight web and document-reading dependencies |
| `requirements-semantic.txt` | Optional semantic-model dependency |
| `requirements-dev.txt` | Additional development and API-test dependencies |
| `setup.ps1` | Creates the virtual environment and installs the base application |
| `run.ps1` | Loads `.env` and starts the local server |
| `test.ps1` | Runs automated tests and syntax compilation |
| `project_tracker.json` | Machine-readable progress shown on the dashboard |
| `PROJECT_TRACKER.md` | Human-readable academic and engineering tracker |
| `docs/PRIVACY.md` | Local retention, deletion controls, and deployment limitations |

## Application package

| Path | Responsibility |
|---|---|
| `app/main.py` | Application factory, startup lifecycle, dependency wiring |
| `app/api/routes.py` | Browser page and `/api` endpoints |
| `app/core/config.py` | Typed configuration and path definitions |
| `app/domain/entities.py` | Data structures shared across layers |
| `app/models/lexical.py` | Lexical similarity features |
| `app/models/semantic.py` | Optional semantic embeddings |
| `app/models/hybrid.py` | Signal fusion and configurable calibrated review bands |
| `app/models/fusion_classifier.py` | Dependency-free logistic-regression feature fusion |
| `app/repositories/corpus.py` | SQLite corpus metadata catalogue |
| `app/repositories/scans.py` | SQLite scan-history and result persistence |
| `app/services/document_extractor.py` | TXT, DOCX, and PDF extraction |
| `app/services/preprocessing.py` | Normalization, tokenization, passage splitting |
| `app/services/file_storage.py` | Upload validation, hashing, safe storage names |
| `app/services/scanner.py` | End-to-end detection orchestration |
| `app/services/report_writer.py` | On-demand Microsoft Word evidence-report generation |
| `app/web/templates/index.html` | Dashboard structure |
| `app/web/static/styles.css` | Responsive visual design |
| `app/web/static/app.js` | API calls and result rendering |

## Data and tests

| Path | Responsibility |
|---|---|
| `data/reference/` | User-provided lawful comparison corpus; ignored by Git |
| `data/uploads/` | Temporary submitted files; deleted after scanning |
| `data/plagiarism_detector.db` | Generated SQLite corpus catalogue; ignored by Git |
| `data/scan_history.db` | Generated SQLite saved-scan database; ignored by Git |
| `tests/` | Unit and service-level regression tests |
| `evaluation/pilot_dataset.json` | Synthetic labelled passage pairs with source-grouped splits |
| `evaluation/metrics.py` | Dependency-free confusion-matrix and threshold metrics |
| `evaluation/runner.py` | Reproducible lexical and optional semantic benchmark |
| `evaluation/charts.py` | Dependency-free SVG generation for model and category results |
| `evaluation/DATASET_PLAN.md` | PAN-PC-11 selection, use constraints, and subset protocol |
| `evaluation/dataset_manifest.json` | Machine-readable dataset provenance and sampling plan |
| `evaluation/pan_adapter.py` | PAN text/XML case extraction, stratified sampling, and grouped splits |
| `evaluation/calibration.py` | Validation-only review-band calibration procedure |
| `evaluation/calibrated_review_bands.json` | Machine-readable deployed pilot thresholds and evidence |
| `evaluation/CALIBRATION_RESULTS.md` | Calibration method, results, limitations, and reproduction command |
| `reports/` | Reserved for generated evaluation and scan reports |
| `logs/` | Reserved for local diagnostic logs |

## Where to implement future features

- Quotation and bibliography exclusions: `app/services/preprocessing.py`.
- TF-IDF candidate retrieval: a new `app/models/retrieval.py` called by `scanner.py`.
- Logistic-regression fusion: a new model in `app/models/fusion_classifier.py`.
- Evaluation metrics and experiments: the top-level `evaluation/` package, not API routes.
- Scan-history retention controls: `app/repositories/scans.py`, `app/api/routes.py`, and `docs/PRIVACY.md`.
- Additional report formats: `app/services/report_writer.py` and the report API route.
