# API Reference

## `GET /api/health`

Returns the application version and whether semantic processing was requested and is available.

## `GET /api/progress`

Returns `project_tracker.json` for the browser dashboard.

## `GET /api/references`

Lists reference-document metadata without exposing stored file paths or contents.

## `POST /api/references`

Multipart field: `file`.

Accepts TXT, DOCX, or text-based PDF files up to the configured size. The response reports passage count and whether the document was already present. SHA-256 hashing prevents duplicate entries.

## `POST /api/scan`

Multipart field: `file`.

Extracts and scans a document, returns component scores and matched passages, and deletes the temporary submitted file after the request.

Important response fields:

- `model_mode`: lexical baseline or hybrid.
- `total_passages`: usable passages in the submission.
- `matched_passages`: passages exceeding the provisional threshold.
- `overall_score`: matched evidence divided by all submitted passages.
- `matches`: source-attributed passage matches and component scores.
- `warnings`: interpretation and calibration limitations.

