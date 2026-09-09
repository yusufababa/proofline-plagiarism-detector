# Explainable Hybrid Plagiarism Detector

A lightweight final-year project for comparing English academic documents with a defined, lawful reference corpus. The software presents traceable textual-similarity evidence for human review; it does not make an automatic finding of academic misconduct.

## Current release

Version `0.2.0` provides:

- TXT, DOCX, and text-based PDF extraction.
- Text normalization and sentence-level passage segmentation.
- A low-memory lexical model with word-cosine and character n-gram scores.
- An optional, lazy-loaded Sentence Transformer interface.
- A transparent hybrid scoring baseline.
- SQLite reference-corpus metadata and duplicate detection.
- Safe temporary upload handling.
- A local dashboard with progress tracking and side-by-side evidence.
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

Detailed setup and troubleshooting are in `docs/SETUP_WINDOWS.md`.

## Project structure

```text
plagiarism-detector/
|-- app/
|   |-- api/             HTTP routes and request validation
|   |-- core/            configuration and paths
|   |-- domain/          shared data structures
|   |-- models/          lexical, semantic, and hybrid algorithms
|   |-- repositories/    SQLite corpus metadata
|   |-- services/        extraction, preprocessing, storage, scanning
|   |-- web/             HTML, CSS, and browser JavaScript
|   `-- main.py          application creation and dependency wiring
|-- data/
|   |-- reference/       lawful source corpus; excluded from Git
|   `-- uploads/         temporary submissions; excluded from Git
|-- docs/                architecture, API, setup, and research notes
|-- logs/                reserved generated logs
|-- reports/             reserved generated reports and evaluation results
|-- tests/               automated regression tests
|-- .env                 active local configuration
|-- .env.example         configuration template
|-- PROJECT_TRACKER.md   detailed build and dissertation tracker
|-- project_tracker.json dashboard progress data
|-- setup.ps1            one-time base installation
|-- run.ps1              local application start
`-- test.ps1             automated checks
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

Begin with fewer than a few hundred short reference documents. Use a cloud notebook or a better-equipped university computer for large evaluation experiments.

## Important research limitation

All score thresholds and hybrid weights are provisional engineering baselines. They must be calibrated and evaluated on labelled data before the dissertation can claim effectiveness. See `docs/RESEARCH_ALIGNMENT.md`.

