from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Passage:
    text: str
    index: int


@dataclass(frozen=True)
class LexicalScore:
    word_cosine: float
    character_jaccard: float
    combined: float


@dataclass(frozen=True)
class ReferenceDocument:
    id: str
    original_name: str
    stored_name: str
    extension: str
    sha256: str
    size_bytes: int
    added_at: str


@dataclass(frozen=True)
class PassageMatch:
    submitted: str
    source: str
    source_document: str
    word_cosine_score: float
    character_jaccard_score: float
    lexical_score: float
    semantic_score: float | None
    hybrid_score: float
    review_band: str


@dataclass
class ScanResult:
    submitted_document: str
    model_mode: str
    total_passages: int
    matched_passages: int
    overall_score: float
    matches: list[PassageMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

