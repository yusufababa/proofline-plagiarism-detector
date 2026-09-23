from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path


class SemanticSimilarityModel:
    """Optional, lazy-loaded semantic model kept out of the base installation."""

    name = "semantic"

    def __init__(self, model_name: str, cache_folder: Path | None = None) -> None:
        self.model_name = model_name
        self.cache_folder = cache_folder
        self._model = None

    @property
    def available(self) -> bool:
        return find_spec("sentence_transformers") is not None

    def _has_cached_snapshot(self) -> bool:
        if not self.cache_folder or not self.cache_folder.exists():
            return False
        return any(self.cache_folder.glob("models--*/snapshots/*/config.json"))

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            if self.cache_folder:
                self.cache_folder.mkdir(parents=True, exist_ok=True)
            self._model = SentenceTransformer(
                self.model_name,
                device="cpu",
                cache_folder=str(self.cache_folder) if self.cache_folder else None,
                local_files_only=self._has_cached_snapshot(),
            )
        return self._model

    def score_many(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        model = self._load()
        submitted = [pair[0] for pair in pairs]
        sources = [pair[1] for pair in pairs]
        submitted_embeddings = model.encode(
            submitted,
            batch_size=4,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        source_embeddings = model.encode(
            sources,
            batch_size=4,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        scores = (submitted_embeddings * source_embeddings).sum(axis=1)
        return [round(max(0.0, min(1.0, float(score))), 4) for score in scores]
