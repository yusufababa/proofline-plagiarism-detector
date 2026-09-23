from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response

from app.core.config import Settings
from app.repositories import CorpusRepository, ScanRepository
from app.services.document_extractor import extract_text
from app.services.file_storage import store_upload, validate_filename
from app.services.preprocessing import split_passages
from app.services.report_writer import build_evidence_report
from app.services.scanner import ScanService


router = APIRouter()


def _services(
    request: Request,
) -> tuple[Settings, CorpusRepository, ScanRepository, ScanService]:
    return (
        request.app.state.settings,
        request.app.state.corpus,
        request.app.state.scans,
        request.app.state.scanner,
    )


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
    config, _, _, scanner = _services(request)
    return {
        "status": "ok",
        "version": config.app_version,
        "semantic_requested": config.semantic_enabled,
        "semantic_available": scanner.semantic.available,
        "review_bands": {
            "lexical": {
                "detection": config.minimum_match_score,
                "medium": config.lexical_medium_review_score,
                "high": config.lexical_high_review_score,
            },
            "hybrid": {
                "detection": config.semantic_minimum_match_score,
                "medium": config.hybrid_medium_review_score,
                "high": config.hybrid_high_review_score,
            },
        },
    }


@router.get("/api/progress")
def progress(request: Request) -> dict:
    config, _, _, _ = _services(request)
    return json.loads(config.tracker_path.read_text(encoding="utf-8"))


@router.get("/api/references")
def references(request: Request) -> dict:
    _, corpus, _, _ = _services(request)
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
    config, corpus, _, _ = _services(request)
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
    config, _, scans, scanner = _services(request)
    filename, content = await _read_upload(file, config)
    try:
        # Submissions are transient. The system temp directory avoids project-folder
        # ownership conflicts and is removed automatically after this request.
        with TemporaryDirectory(prefix="proofline-upload-") as temporary_directory:
            stored = store_upload(
                filename,
                content,
                Path(temporary_directory),
                config.allowed_extensions,
            )
            text = extract_text(stored.path, config.allowed_extensions)
            result = scanner.scan_text(filename, text)
            record = scans.save(result)
            payload = result.to_dict()
            payload.update(
                {
                    "scan_id": record.id,
                    "created_at": record.created_at,
                    "report_url": f"/api/scans/{record.id}/report",
                }
            )
            return payload
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except OSError as exc:
        raise HTTPException(
            500,
            "Temporary storage is unavailable. Restart Proofline and try the scan again.",
        ) from exc
    except Exception as exc:
        raise HTTPException(500, f"The scan could not be completed: {exc}") from exc


@router.get("/api/scans")
def scan_history(request: Request, limit: int = 20) -> dict:
    _, _, scans, _ = _services(request)
    records = scans.list_recent(limit)
    return {
        "count": len(records),
        "scans": [
            {
                **record.__dict__,
                "detail_url": f"/api/scans/{record.id}",
                "report_url": f"/api/scans/{record.id}/report",
            }
            for record in records
        ],
    }


@router.get("/api/scans/{scan_id}")
def scan_detail(request: Request, scan_id: str) -> dict:
    _, _, scans, _ = _services(request)
    result = scans.get_result(scan_id)
    if result is None:
        raise HTTPException(404, "The saved scan was not found.")
    return result


@router.get("/api/scans/{scan_id}/report")
def download_report(request: Request, scan_id: str) -> Response:
    _, _, scans, _ = _services(request)
    result = scans.get_result(scan_id)
    if result is None:
        raise HTTPException(404, "The saved scan was not found.")
    report = build_evidence_report(result)
    return Response(
        content=report,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="proofline-report-{scan_id[:12]}.docx"'
        },
    )


@router.delete("/api/scans/{scan_id}")
def delete_scan(request: Request, scan_id: str) -> dict:
    _, _, scans, _ = _services(request)
    if not scans.delete(scan_id):
        raise HTTPException(404, "The saved scan was not found.")
    return {"message": "Saved scan deleted.", "scan_id": scan_id}


@router.delete("/api/scans")
def clear_scan_history(request: Request) -> dict:
    _, _, scans, _ = _services(request)
    deleted = scans.clear()
    return {"message": "Saved scan history cleared.", "deleted": deleted}
