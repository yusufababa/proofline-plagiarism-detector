"""Domain objects shared by the application layers."""

from app.domain.entities import (
    LexicalScore,
    Passage,
    PassageMatch,
    ReferenceDocument,
    ScanResult,
)

__all__ = [
    "LexicalScore",
    "Passage",
    "PassageMatch",
    "ReferenceDocument",
    "ScanResult",
]

