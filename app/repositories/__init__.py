"""Persistence adapters."""

from app.repositories.corpus import CorpusRepository
from app.repositories.scans import ScanRepository

__all__ = ["CorpusRepository", "ScanRepository"]
