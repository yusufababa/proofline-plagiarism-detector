from __future__ import annotations

from app.core.config import Settings
from app.domain import LexicalScore, PassageMatch, ScanResult
from app.models import (
    HybridSimilarityModel,
    LexicalSimilarityModel,
    SemanticSimilarityModel,
    review_band,
)
from app.repositories import CorpusRepository
from app.services.document_extractor import extract_text
from app.services.preprocessing import normalize_text, split_passages


class ScanService:
    """Coordinates extraction, candidate matching, scoring, and reporting."""

    def __init__(self, config: Settings, corpus: CorpusRepository) -> None:
        self.config = config
        self.corpus = corpus
        self.lexical = LexicalSimilarityModel()
        self.semantic = SemanticSimilarityModel(config.semantic_model_name)
        self.hybrid = HybridSimilarityModel(config.lexical_weight, config.semantic_weight)

    def _reference_passages(self) -> list[tuple[str, str]]:
        passages: list[tuple[str, str]] = []
        for document in self.corpus.list_all():
            path = self.corpus.path_for(document)
            if not path.exists():
                continue
            try:
                text = extract_text(path, self.config.allowed_extensions)
            except Exception:
                continue
            passages.extend(
                (document.original_name, passage.text)
                for passage in split_passages(text, self.config.minimum_passage_words)
            )
        return passages

    def scan_text(self, document_name: str, text: str) -> ScanResult:
        submitted = split_passages(text, self.config.minimum_passage_words)
        references = self._reference_passages()
        if not references:
            raise ValueError("Add at least one readable reference document before scanning.")
        if not submitted:
            raise ValueError("No usable text was found in the submitted document.")

        candidates: list[tuple[str, str, str, LexicalScore]] = []
        for passage in submitted:
            best = None
            for source_document, source_text in references:
                lexical = self.lexical.score(passage.text, source_text)
                if best is None or lexical.combined > best[2].combined:
                    best = (source_document, source_text, lexical)
            if best and best[2].combined >= self.config.minimum_match_score:
                candidates.append((passage.text, best[0], best[1], best[2]))

        semantic_scores: list[float | None] = [None] * len(candidates)
        semantic_active = self.config.semantic_enabled and self.semantic.available
        if semantic_active:
            pairs = [(item[0], item[2]) for item in candidates]
            semantic_scores = self.semantic.score_many(pairs)

        matches: list[PassageMatch] = []
        for candidate, semantic_score in zip(candidates, semantic_scores, strict=True):
            submitted_text, source_document, source_text, lexical = candidate
            hybrid_score = self.hybrid.score(lexical.combined, semantic_score)
            matches.append(
                PassageMatch(
                    submitted=normalize_text(submitted_text),
                    source=normalize_text(source_text),
                    source_document=source_document,
                    word_cosine_score=lexical.word_cosine,
                    character_jaccard_score=lexical.character_jaccard,
                    lexical_score=lexical.combined,
                    semantic_score=semantic_score,
                    hybrid_score=hybrid_score,
                    review_band=review_band(hybrid_score),
                )
            )

        matches.sort(key=lambda item: item.hybrid_score, reverse=True)
        overall = sum(match.hybrid_score for match in matches) / len(submitted)
        warnings = [
            "Thresholds are provisional and must be calibrated during Objective 3.",
            "Similarity is evidence for human review, not a misconduct decision.",
        ]
        if self.config.semantic_enabled and not self.semantic.available:
            warnings.append("Semantic mode was requested but its optional package is not installed.")

        return ScanResult(
            submitted_document=document_name,
            model_mode="hybrid" if semantic_active else "lexical baseline",
            total_passages=len(submitted),
            matched_passages=len(matches),
            overall_score=round(overall, 4),
            matches=matches,
            warnings=warnings,
        )
