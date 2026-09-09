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
      -> explainable JSON result
  -> side-by-side result display
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
- `app/models/hybrid.py` combines lexical and semantic evidence and assigns provisional review bands.

### Service layer

- `document_extractor.py` reads TXT, DOCX, and text-based PDF documents.
- `preprocessing.py` normalizes text, tokenizes it, and splits it into passages.
- `file_storage.py` validates and safely names uploads.
- `scanner.py` coordinates the complete detection workflow.

### Repository layer

`app/repositories/corpus.py` stores source-document metadata in SQLite while leaving original document bytes on disk. SHA-256 hashes prevent duplicate corpus entries.

### Web layer

`app/web/` contains the HTML, CSS, and JavaScript interface. The interface only calls documented API endpoints.

## Current algorithm

For each submitted passage, the scanner compares all reference passages and retains the highest lexical candidate above the provisional threshold. The lexical score is:

```text
lexical = 0.70 * word cosine + 0.30 * character 4-gram Jaccard
```

When semantic mode is enabled, semantic similarity is calculated only for the shortlisted lexical candidates. This reduces RAM and CPU use. The provisional hybrid score is:

```text
hybrid = 0.55 * lexical + 0.45 * semantic
```

Both formulas are baselines. The project evaluation must compare them with calibrated or learned alternatives before presenting them as final.

