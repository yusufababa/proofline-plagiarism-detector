from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings with conservative defaults for a 4 GB laptop."""

    project_root: Path
    app_name: str = "Explainable Hybrid Plagiarism Detector"
    app_version: str = "0.12.0"
    host: str = "127.0.0.1"
    port: int = 8000
    max_upload_mb: int = 10
    minimum_passage_words: int = 5
    minimum_match_score: float = 0.15
    semantic_minimum_match_score: float = 0.20
    lexical_medium_review_score: float = 0.25
    lexical_high_review_score: float = 0.69
    hybrid_medium_review_score: float = 0.46
    hybrid_high_review_score: float = 0.80
    lexical_weight: float = 0.55
    semantic_weight: float = 0.45
    semantic_enabled: bool = False
    semantic_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    @classmethod
    def from_environment(cls, project_root: Path | None = None) -> "Settings":
        root = project_root or Path(__file__).resolve().parents[2]
        return cls(
            project_root=root,
            host=os.getenv("APP_HOST", "127.0.0.1"),
            port=int(os.getenv("APP_PORT", "8000")),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "10")),
            minimum_passage_words=int(os.getenv("MINIMUM_PASSAGE_WORDS", "5")),
            minimum_match_score=float(os.getenv("MINIMUM_MATCH_SCORE", "0.15")),
            semantic_minimum_match_score=float(
                os.getenv("SEMANTIC_MINIMUM_MATCH_SCORE", "0.20")
            ),
            lexical_medium_review_score=float(
                os.getenv("LEXICAL_MEDIUM_REVIEW_SCORE", "0.25")
            ),
            lexical_high_review_score=float(
                os.getenv("LEXICAL_HIGH_REVIEW_SCORE", "0.69")
            ),
            hybrid_medium_review_score=float(
                os.getenv("HYBRID_MEDIUM_REVIEW_SCORE", "0.46")
            ),
            hybrid_high_review_score=float(
                os.getenv("HYBRID_HIGH_REVIEW_SCORE", "0.80")
            ),
            lexical_weight=float(os.getenv("LEXICAL_WEIGHT", "0.55")),
            semantic_weight=float(os.getenv("SEMANTIC_WEIGHT", "0.45")),
            semantic_enabled=_as_bool(os.getenv("SEMANTIC_ENABLED"), False),
            semantic_model_name=os.getenv(
                "SEMANTIC_MODEL_NAME",
                "sentence-transformers/all-MiniLM-L6-v2",
            ),
        )

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def reference_dir(self) -> Path:
        return self.data_dir / "reference"

    @property
    def upload_dir(self) -> Path:
        return self.data_dir / "uploads"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "plagiarism_detector.db"

    @property
    def scan_database_path(self) -> Path:
        return self.data_dir / "scan_history.db"

    @property
    def semantic_cache_dir(self) -> Path:
        configured = os.getenv("SEMANTIC_CACHE_DIR")
        return Path(configured).expanduser() if configured else self.data_dir / "models"

    @property
    def tracker_path(self) -> Path:
        return self.project_root / "project_tracker.json"

    @property
    def web_dir(self) -> Path:
        return self.project_root / "app" / "web"

    @property
    def template_dir(self) -> Path:
        return self.web_dir / "templates"

    @property
    def static_dir(self) -> Path:
        return self.web_dir / "static"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def allowed_extensions(self) -> frozenset[str]:
        return frozenset({".txt", ".docx", ".pdf"})

    def prepare_directories(self) -> None:
        for directory in (self.data_dir, self.reference_dir, self.upload_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        if self.max_upload_mb < 1:
            raise ValueError("MAX_UPLOAD_MB must be at least 1.")
        if not 0 <= self.minimum_match_score <= 1:
            raise ValueError("MINIMUM_MATCH_SCORE must be between 0 and 1.")
        if not 0 <= self.semantic_minimum_match_score <= 1:
            raise ValueError("SEMANTIC_MINIMUM_MATCH_SCORE must be between 0 and 1.")
        review_ranges = (
            (
                self.minimum_match_score,
                self.lexical_medium_review_score,
                self.lexical_high_review_score,
                "lexical",
            ),
            (
                self.semantic_minimum_match_score,
                self.hybrid_medium_review_score,
                self.hybrid_high_review_score,
                "hybrid",
            ),
        )
        for detection, medium, high, name in review_ranges:
            if not 0 <= detection <= medium < high <= 1:
                raise ValueError(
                    f"The {name} thresholds must satisfy detection <= medium < high <= 1."
                )
        if not 0 <= self.lexical_weight <= 1 or not 0 <= self.semantic_weight <= 1:
            raise ValueError("Model weights must be between 0 and 1.")
        if abs((self.lexical_weight + self.semantic_weight) - 1.0) > 1e-9:
            raise ValueError("LEXICAL_WEIGHT and SEMANTIC_WEIGHT must sum to 1.0.")


settings = Settings.from_environment()
settings.validate()
settings.prepare_directories()
