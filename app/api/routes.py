from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse

from app.core.config import Settings
from app.repositories import CorpusRepository
from app.services.document_extractor import extract_text
from app.services.file_storage import store_upload, validate_filename
from app.services.preprocessing import split_passages
from app.services.scanner import ScanService


router = APIRouter()


def _services(request: Request) -> tuple[Settings, CorpusRepository, ScanService]:
    return request.app.state.settings, request.app.state.corpus, request.app.state.scanner


async def _read_upload(upload: UploadFile, config: Settings) -> tuple[str, bytes]:
    try:
        filename = validate_filename(upload.filename, config.allowed_extensions)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    content = await upload.read(config.max_upload_bytes + 1)
    if not content:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(content) > config.max_upload_bytes:
        raise HTTPException(413, f"The maximum file size is {config.max_upload_mb} MB.")
    return filename, content


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    config: Settings = request.app.state.settings
    return HTMLResponse((config.template_dir / "index.html").read_text(encoding="utf-8"))


@router.get("/api/health")
def health(request: Request) -> dict:
    config, _, scanner = _services(request)
    return {
        "status": "ok",
        "version": config.app_version,
        "semantic_requested": config.semantic_enabled,
        "semantic_available": scanner.semantic.available,
    }


@router.get("/api/progress")
def progress(request: Request) -> dict:
    config, _, _ = _services(request)
    return json.loads(config.tracker_path.read_text(encoding="utf-8"))


@router.get("/api/references")
def references(request: Request) -> dict:
    _, corpus, _ = _services(request)
    documents = corpus.list_all()
    return {
        "count": len(documents),
        "documents": [
            {
                "id": item.id,
                "name": item.original_name,
                "extension": item.extension,
                "size_bytes": item.size_bytes,
                "added_at": item.added_at,
            }
            for item in documents
        ],
    }


@router.post("/api/references")
async def add_reference(request: Request, file: UploadFile = File(...)) -> dict:
    config, corpus, _ = _services(request)
    filename, content = await _read_upload(file, config)
    digest = hashlib.sha256(content).hexdigest()
    duplicate = corpus.find_by_hash(digest)
    if duplicate:
        return {
            "message": "This reference is already in the corpus.",
            "name": duplicate.original_name,
            "duplicate": True,
        }

    stored = store_upload(filename, content, config.reference_dir, config.allowed_extensions)
    try:
        text = extract_text(stored.path, config.allowed_extensions)
        passage_count = len(split_passages(text, config.minimum_passage_words))
        if passage_count == 0:
            raise ValueError("No usable text was found in the document.")
        document = corpus.add(stored.original_name, stored.stored_name, content)
    except Exception as exc:
        stored.path.unlink(missing_ok=True)
        raise HTTPException(400, f"The document could not be added: {exc}") from exc

    return {
        "message": "Reference document added.",
        "id": document.id,
        "name": document.original_name,
        "passages": passage_count,
        "duplicate": False,
    }


@router.post("/api/scan")
async def scan(request: Request, file: UploadFile = File(...)) -> dict:
    config, _, scanner = _services(request)
    filename, content = await _read_upload(file, config)
    stored = store_upload(filename, content, config.upload_dir, config.allowed_extensions)
    try:
        text = extract_text(stored.path, config.allowed_extensions)
        return scanner.scan_text(filename, text).to_dict()
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(500, f"The scan could not be completed: {exc}") from exc
    finally:
        stored.path.unlink(missing_ok=True)

