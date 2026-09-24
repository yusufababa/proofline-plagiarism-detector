# Explainable Hybrid Plagiarism Detector

A lightweight final-year project for comparing English academic documents with a defined, lawful reference corpus. The software presents traceable textual-similarity evidence for human review; it does not make an automatic finding of academic misconduct.

## Current release

Version `0.13.1` release candidate provides:

- TXT, DOCX, and text-based PDF extraction.
- Text normalization and sentence-level passage segmentation.
- Bibliography removal, simple boilerplate filtering, and citation-aware quotation handling.
- A low-memory lexical model with word-cosine and character n-gram scores.
- An optional, lazy-loaded Sentence Transformer interface.
- A transparent hybrid scoring baseline.
- SQLite reference-corpus metadata and duplicate detection.
- Safe temporary upload handling.
- A focused dashboard with scan history, source management, and side-by-side evidence.
- A Satoshi-led monochrome welcome composer with pasted-text, file-upload, and drag-and-drop scanning.
- A responsive results workspace with Overview, Evidence, History, and Source Library navigation.
- Visible citation and quotation flags with transparent overall-score exclusions.
- A leakage-safe synthetic pilot dataset and dependency-free evaluation runner.
- Precision, recall, F1, false-positive, runtime, and memory measurements.
- A verified CPU-only MiniLM benchmark and lexical/semantic/hybrid comparison.
- A configurable project-local semantic-model cache for Windows.
- Offline-first semantic loading when a complete cached snapshot is present.
- Validation-only calibration of lexical and hybrid evidence-priority bands.
- Configurable detection, medium-review, and high-review thresholds.
- Individual and clear-all controls for locally saved scan history.
- A documented local-data retention model with no submitted-file retention.
- Keyboard skip navigation, visible focus indicators, live regions, and reduced-motion support.
- Dependency-free logistic-regression fusion training with exported coefficients.
- Leakage-safe comparison of learned fusion against the weighted baseline.
- Category-level error analysis and automatically generated SVG charts.
- A documented PAN-PC-11 research-dataset and laptop-safe subset plan.
- A tested PAN text/XML import adapter with safe offsets and English filtering.
- Deterministic, category-balanced sampling and source-grouped data splits.
- Persistent local scan history backed by SQLite.
- Downloadable Microsoft Word evidence reports with source passages and model signals.
- A lecturer-ready technical report and demonstration documents under `lecturer_demo/`.
- A one-command release-readiness check for tests, syntax, versions, metadata, and report integrity.
- A Render Blueprint with a fixed Python runtime, health check, protected access, and seeded demo corpus.
- Unit and service-level automated tests.

## Quick start on Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\run.ps1
```

Open `http://127.0.0.1:8000`. Add lawful reference documents before scanning a submission.

Run all checks with:

```powershell
.\test.ps1
```

Run the complete release-readiness check with:

```powershell
.\verify_release.ps1
```

Detailed setup and troubleshooting are in `docs/SETUP_WINDOWS.md`.
Local storage, deletion controls, and deployment limitations are explained in `docs/PRIVACY.md`.

## Deploy the protected demo to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yusufababa/proofline-plagiarism-detector)

The checked-in `render.yaml` deploys the lightweight lexical version on Render's free web-service plan. During Blueprint creation, Render asks for `APP_ACCESS_PASSWORD`. Share that password and the username `proofline` only with the lecturer.

The hosted demo writes to the configurable `DATA_DIR` and automatically loads the bundled lecturer corpus after a fresh start. The free filesystem is temporary, so newly uploaded reference documents and scan history can disappear after a restart or redeploy. A paid Render service with a persistent disk is required for durable hosted data. MiniLM is deliberately disabled on the 512 MB free service; use the 2 GB plan and install `requirements-semantic.txt` before enabling it.

Render production commands are already defined as:

```text
Build: pip install --upgrade pip && pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health: /api/health
```

## Run the model evaluation

The low-memory lexical benchmark runs without installing BERT or MiniLM:

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner
```

The generated readable and machine-readable results are saved under `reports/`. Checked-in interpretations and figures are under `evaluation/`, including `ANALYSIS_RESULTS.md` and `DATASET_PLAN.md`. See `evaluation/README.md` for the comparison command and research limitations.

## Project structure

```text
plagiarism-detector/
|-- app/
|   |-- api/             HTTP routes and request validation
|   |-- core/            configuration and paths
|   |-- domain/          shared data structures
|   |-- models/          lexical, semantic, and hybrid algorithms
|   |-- repositories/    SQLite corpus metadata and saved scan history
|   |-- services/        extraction, preprocessing, storage, scanning
|   |-- web/             HTML, CSS, and browser JavaScript
|   `-- main.py          application creation and dependency wiring
|-- data/
|   |-- reference/       lawful source corpus; excluded from Git
|   `-- uploads/         temporary submissions; excluded from Git
|-- docs/                architecture, API, setup, and research notes
|-- evaluation/          labelled pilot data, metrics, and experiment runner
|-- logs/                reserved generated logs
|-- reports/             generated evaluation results
|-- tests/               automated regression tests
|-- .env                 active local configuration
|-- .env.example         configuration template
|-- PROJECT_TRACKER.md   detailed build and dissertation tracker
|-- project_tracker.json dashboard progress data
|-- setup.ps1            one-time base installation
|-- run.ps1              local application start
|-- test.ps1             automated checks
`-- verify_release.ps1   final release-readiness verification
```

Every source file is explained in `docs/SOURCE_CODE_GUIDE.md`. The technical flow and formulas are documented in `docs/ARCHITECTURE.md`.

## Low-memory operating mode

The base configuration is intended for a 4 GB laptop:

- Semantic processing is off by default.
- No Docker, PostgreSQL, Redis, React build process, or background worker is required.
- Reference metadata uses built-in SQLite.
- Only the best lexical candidate is sent to the optional semantic stage.
- Semantic batches are limited to four pairs.
- Submitted files are deleted after scanning.
- Saved history contains the submitted filename and evidence result, not the uploaded file.

Begin with fewer than a few hundred short reference documents. Use a cloud notebook or a better-equipped university computer for large evaluation experiments.

## Important research limitation

The live thresholds now reproduce the synthetic pilot validation calibration, but they are not final effectiveness evidence. They must be recalibrated and evaluated on the larger independently reviewed research dataset before the dissertation makes general claims. See `evaluation/CALIBRATION_RESULTS.md` and `docs/RESEARCH_ALIGNMENT.md`.
