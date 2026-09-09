from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings
from app.repositories import CorpusRepository
from app.services.scanner import ScanService


@asynccontextmanager
async def lifespan(app: FastAPI):
    corpus = CorpusRepository(settings.database_path, settings.reference_dir)
    corpus.initialize()
    corpus.sync_existing_files(settings.allowed_extensions)
    app.state.settings = settings
    app.state.corpus = corpus
    app.state.scanner = ScanService(settings, corpus)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Explainable text-similarity decision support for academic review.",
        lifespan=lifespan,
    )
    application.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
    application.include_router(router)
    return application


app = create_app()

