# System Architecture

## Design goals

The architecture keeps the research algorithms independent from the browser and storage code. This allows the same lexical, semantic, and hybrid models to be evaluated from scripts later without starting the web application.

The base system is deliberately small enough for a 4 GB Windows laptop: one Python process, SQLite metadata, disk-based source documents, no Docker, and semantic processing disabled by default.

## Request flow

```text
Browser
  -> FastAPI routes
      -> upload validation and temporary storage
      -> document extraction
      -> passage preprocessing
      -> scan service
          -> corpus repository
          -> lexical model
          -> optional semantic model
          -> hybrid model
      -> scan-history repository
      -> explainable JSON result
  -> side-by-side result display / saved-history view / Word report
```

## Layers

### API layer

`app/api/routes.py` owns HTTP request validation and responses. It does not contain similarity formulas or database queries.

### Core layer

`app/core/config.py` owns environment configuration, paths, upload limits, thresholds, and low-memory defaults.

### Domain layer

`app/domain/entities.py` defines the data exchanged between layers: passages, component scores, reference documents, matches, and scan results.

### Model layer

- `app/models/lexical.py` calculates word cosine, character n-gram Jaccard, and a combined lexical score.
- `app/models/semantic.py` lazily loads the optional sentence-embedding model.
- `app/models/hybrid.py` combines lexical and semantic evidence and assigns validation-calibrated review bands.
- `app/models/fusion_classifier.py` learns logistic-regression coefficients from labelled features for evaluation.

### Service layer

- `document_extractor.py` reads TXT, DOCX, and text-based PDF documents.
- `preprocessing.py` normalizes text, tokenizes it, and splits it into passages.
- `file_storage.py` validates and safely names uploads.
- `scanner.py` coordinates the complete detection workflow.
- `report_writer.py` generates Microsoft Word evidence reports from saved results.

### Repository layer

- `app/repositories/corpus.py` stores source-document metadata in SQLite while leaving original document bytes on disk. SHA-256 hashes prevent duplicate corpus entries.
- `app/repositories/scans.py` stores result summaries and complete explainable JSON payloads in a separate local SQLite file. Uploaded submissions are not retained.

The scan repository also supports explicit single-record and clear-all deletion. The web interface requires confirmation before invoking these destructive operations. This is appropriate for the localhost prototype; multi-user deployment remains out of scope without authentication and institutional retention controls.

### Web layer

`app/web/` contains the HTML, CSS, and JavaScript interface. The interface only calls documented API endpoints.

## Current algorithm

For each submitted passage, the scanner compares all reference passages and retains the highest lexical candidate. In lexical-only mode, that candidate must pass the pilot-calibrated lexical threshold. The lexical score is:

```text
lexical = 0.70 * word cosine + 0.30 * character 4-gram Jaccard
```

When semantic mode is enabled, the single best lexical candidate per submitted passage is sent to MiniLM even if it is below the lexical threshold. This allows semantic evidence to recover low-overlap paraphrases without embedding every corpus pair. The transparent hybrid score is:

```text
hybrid = 0.55 * lexical + 0.45 * semantic
```

The synthetic validation split selected detection floors of `0.15` for lexical mode and `0.20` for hybrid mode. Review-priority boundaries are `0.25`/`0.69` for lexical and `0.46`/`0.80` for hybrid. The procedure and evidence are documented in `evaluation/CALIBRATION_RESULTS.md`. These pilot values must be recalibrated on the final research dataset.

Both formulas are baselines. The project evaluation must compare them with calibrated or learned alternatives before presenting them as final.

The evaluation runner also fits logistic regression using word-cosine, character-Jaccard, and semantic scores from the training split. Validation data selects its threshold, and the test split is used only for the final comparison. Because the pilot training set is very small, the learned coefficients are exported for research inspection but are not used by the live scanner.
