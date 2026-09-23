from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Passage:
    text: str
    index: int
    is_quotation: bool = False
    has_citation: bool = False


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
class ScanRecord:
    id: str
    submitted_document: str
    created_at: str
    model_mode: str
    overall_score: float
    total_passages: int
    matched_passages: int
    reviewable_passages: int
    excluded_passages: int


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
    is_quotation: bool = False
    has_citation: bool = False
    excluded_from_overall: bool = False


@dataclass
class ScanResult:
    submitted_document: str
    model_mode: str
    total_passages: int
    matched_passages: int
    reviewable_passages: int
    excluded_passages: int
    overall_score: float
    review_thresholds: dict[str, float] = field(default_factory=dict)
    matches: list[PassageMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
