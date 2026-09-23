# API Reference

## `GET /api/health`

Returns the application version, whether semantic processing was requested and is available, and the deployed lexical and hybrid review-band thresholds.

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
- `matched_passages`: passages exceeding the mode-specific detection threshold.
- `reviewable_passages`: passages included in the overall-score denominator.
- `excluded_passages`: properly cited quotation passages excluded from the overall score.
- `overall_score`: included matched evidence divided by reviewable submitted passages.
- `matches`: source-attributed passage matches, component scores, citation flags, and exclusion status.
- `warnings`: interpretation and calibration limitations.
- `scan_id`: identifier for reopening the saved evidence.
- `report_url`: endpoint for downloading the Word report.
- `review_thresholds`: the detection, medium, and high boundaries applied to the scan.

Successful scan results are saved in the local SQLite database. The uploaded submission file is still deleted after processing.

## `GET /api/scans`

Lists recent saved scan summaries. An optional `limit` query parameter is constrained to between 1 and 100 records.

## `GET /api/scans/{scan_id}`

Returns the complete saved result for one scan so the browser can reopen its evidence view.

## `GET /api/scans/{scan_id}/report`

Generates and downloads a Microsoft Word `.docx` evidence report containing the scan summary, interpretation notice, source-attributed passages, component scores, and citation flags.

## `DELETE /api/scans/{scan_id}`

Permanently removes one saved scan result. It does not modify reference documents.

## `DELETE /api/scans`

Permanently clears all saved scan results and returns the number deleted. The browser asks for confirmation before calling either deletion endpoint.
