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

## Hosted demonstration

Local use remains open on `127.0.0.1`. A hosted deployment can set `APP_ACCESS_PASSWORD` to enable application-wide HTTP Basic authentication; `APP_ACCESS_USERNAME` defaults to `proofline`. The Render Blueprint requires a password and leaves only `/api/health` unprotected for platform health checks.

This protection is suitable for a limited lecturer demonstration, not a production institutional service. Do not upload confidential student work to a public or shared deployment. A true multi-user deployment still requires individual accounts, authorization, institutional retention rules, an audit log, and a durable managed datastore.

On Render's free service, SQLite databases and added reference files use an ephemeral filesystem and can be lost after a restart or redeploy. The bundled non-private lecturer corpus can be restored automatically with `SEED_DEMO_CORPUS=true`. Durable hosted history requires a paid persistent disk or migration to a managed database.
