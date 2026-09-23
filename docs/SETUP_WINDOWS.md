# Windows Setup Guide

## Requirements

- Windows 10 or 11.
- Python 3.11 or newer, including the `py` launcher.
- Internet access during initial package installation.
- At least 4 GB RAM and approximately 2 GB free storage for the base version.

## First setup

Open PowerShell in the project folder and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
```

The script creates `.venv`, installs only the lightweight requirements, and creates `.env` when needed. If the download fails, reconnect to a stable network and run the same command again.

## Start the application

```powershell
.\run.ps1
```

Open `http://127.0.0.1:8000`. Stop the server with `Ctrl+C`.

## Run checks

```powershell
.\test.ps1
```

## Optional semantic model

Only enable this after the lexical version works reliably:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt
```

Then set `SEMANTIC_ENABLED=true` in `.env` and restart the application. Keep `SEMANTIC_MINIMUM_MATCH_SCORE=0.20` for the current pilot-calibrated hybrid threshold. The first semantic scan downloads about 87 MB of model files; set `SEMANTIC_CACHE_DIR` if the default `data/models` folder is not writable.

The verified cached pilot used about 503 MB peak process memory, and the completed semantic-enabled virtual environment occupied about 1.02 GB on disk. On a 4 GB laptop, close browsers and other heavy applications before scanning with semantic mode. Set `SEMANTIC_ENABLED=false` whenever the lighter lexical-only mode is preferred.

## Common problems

- `Python is not recognized`: install Python and enable the launcher during installation.
- PowerShell blocks scripts: run the process-scoped execution-policy command above.
- Required packages are missing: rerun `setup.ps1` with a stable connection.
- A PDF produces no text: it is probably scanned imagery and requires OCR, which is outside the first version.
- The laptop becomes slow: disable semantic mode, close other applications, and reduce the corpus size.
