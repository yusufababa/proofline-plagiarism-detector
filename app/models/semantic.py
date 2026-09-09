from __future__ import annotations


class SemanticSimilarityModel:
    """Optional, lazy-loaded semantic model kept out of the base installation."""

    name = "semantic"

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    @property
    def available(self) -> bool:
        try:
            import sentence_transformers  # noqa: F401
        except ImportError:
            return False
        return True

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device="cpu")
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

