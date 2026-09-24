from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.security import BasicAccessMiddleware
from app.core.config import settings
from app.repositories import CorpusRepository, ScanRepository
from app.services.demo_data import seed_demo_references
from app.services.scanner import ScanService


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.seed_demo_corpus:
        seed_demo_references(settings)
    corpus = CorpusRepository(settings.database_path, settings.reference_dir)
    corpus.initialize()
    corpus.sync_existing_files(settings.allowed_extensions)
    scans = ScanRepository(settings.scan_database_path)
    scans.initialize()
    app.state.settings = settings
    app.state.corpus = corpus
    app.state.scans = scans
    app.state.scanner = ScanService(settings, corpus)
    yield


def create_app() -> FastAPI:
    required_assets = (
        settings.static_dir / "styles.css",
        settings.static_dir / "app.js",
        settings.template_dir / "index.html",
    )
    missing_assets = [str(path) for path in required_assets if not path.is_file()]
    if missing_assets:
        raise RuntimeError(f"Required web assets are missing: {', '.join(missing_assets)}")

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Explainable text-similarity decision support for academic review.",
        lifespan=lifespan,
    )
    application.add_middleware(
        BasicAccessMiddleware,
        username=settings.access_username,
        password=settings.access_password,
        excluded_paths=frozenset({"/api/health"}),
    )
    application.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    application.include_router(router)
    return application


app = create_app()
