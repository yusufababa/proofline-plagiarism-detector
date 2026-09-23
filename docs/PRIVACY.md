# Local Privacy and Data Retention

Proofline is a single-user localhost research prototype. It binds to `127.0.0.1` by default and does not include user accounts or remote sharing.

## What is retained

- Reference documents remain in `data/reference/` until the user removes them from the project data folder.
- Reference metadata and file hashes are stored in `data/plagiarism_detector.db`.
- A completed scan retains the submitted filename, calculated scores, matched text passages, source names, warnings, and timestamps in `data/scan_history.db`.

## What is not retained

- The uploaded submission file is removed from `data/uploads/` in a `finally` block after processing, including when a scan fails.
- Word reports are generated on demand and are not automatically stored by the server.
- Cached MiniLM model files contain the model, not submitted documents.

## User controls

The Recent scan history section provides:

- **Delete** to remove one saved scan result.
- **Clear all history** to remove every saved scan result.

Both actions require browser confirmation and cannot be undone. The API equivalents are `DELETE /api/scans/{scan_id}` and `DELETE /api/scans`.

## Deployment limitation

There is no authentication because the current application is designed for one person on one local Windows computer. Do not expose the server to a public or shared network. A multi-user deployment would require authentication, authorization, encrypted transport, institutional retention rules, and an audit log.
