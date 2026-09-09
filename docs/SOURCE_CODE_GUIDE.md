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

## Application package

| Path | Responsibility |
|---|---|
| `app/main.py` | Application factory, startup lifecycle, dependency wiring |
| `app/api/routes.py` | Browser page and `/api` endpoints |
| `app/core/config.py` | Typed configuration and path definitions |
| `app/domain/entities.py` | Data structures shared across layers |
| `app/models/lexical.py` | Lexical similarity features |
| `app/models/semantic.py` | Optional semantic embeddings |
| `app/models/hybrid.py` | Signal fusion and provisional review bands |
| `app/repositories/corpus.py` | SQLite corpus metadata catalogue |
| `app/services/document_extractor.py` | TXT, DOCX, and PDF extraction |
| `app/services/preprocessing.py` | Normalization, tokenization, passage splitting |
| `app/services/file_storage.py` | Upload validation, hashing, safe storage names |
| `app/services/scanner.py` | End-to-end detection orchestration |
| `app/web/templates/index.html` | Dashboard structure |
| `app/web/static/styles.css` | Responsive visual design |
| `app/web/static/app.js` | API calls and result rendering |

## Data and tests

| Path | Responsibility |
|---|---|
| `data/reference/` | User-provided lawful comparison corpus; ignored by Git |
| `data/uploads/` | Temporary submitted files; deleted after scanning |
| `data/plagiarism_detector.db` | Generated SQLite corpus catalogue; ignored by Git |
| `tests/` | Unit and service-level regression tests |
| `reports/` | Reserved for generated evaluation and scan reports |
| `logs/` | Reserved for local diagnostic logs |

## Where to implement the next features

- Quotation and bibliography exclusions: `app/services/preprocessing.py`.
- TF-IDF candidate retrieval: a new `app/models/retrieval.py` called by `scanner.py`.
- Logistic-regression fusion: a new model in `app/models/fusion_classifier.py`.
- Evaluation metrics: a future top-level `evaluation/` package, not API routes.
- Saved scan history: a new repository under `app/repositories/`.
- Downloadable reports: a new service under `app/services/` and a small API route.

