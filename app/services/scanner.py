from __future__ import annotations

from app.core.config import Settings
from app.domain import LexicalScore, Passage, PassageMatch, ScanResult
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
        self.semantic = SemanticSimilarityModel(
            config.semantic_model_name,
            cache_folder=config.semantic_cache_dir,
        )
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

        semantic_active = self.config.semantic_enabled and self.semantic.available
        active_threshold = (
            self.config.semantic_minimum_match_score
            if semantic_active
            else self.config.minimum_match_score
        )
        medium_review_score = (
            self.config.hybrid_medium_review_score
            if semantic_active
            else self.config.lexical_medium_review_score
        )
        high_review_score = (
            self.config.hybrid_high_review_score
            if semantic_active
            else self.config.lexical_high_review_score
        )
        candidates: list[tuple[Passage, str, str, LexicalScore]] = []
        for passage in submitted:
            best = None
            for source_document, source_text in references:
                lexical = self.lexical.score(passage.text, source_text)
                if best is None or lexical.combined > best[2].combined:
                    best = (source_document, source_text, lexical)
            if best and (semantic_active or best[2].combined >= active_threshold):
                candidates.append((passage, best[0], best[1], best[2]))

        semantic_scores: list[float | None] = [None] * len(candidates)
        if semantic_active:
            pairs = [(item[0].text, item[2]) for item in candidates]
            semantic_scores = self.semantic.score_many(pairs)

        matches: list[PassageMatch] = []
        for candidate, semantic_score in zip(candidates, semantic_scores, strict=True):
            submitted_passage, source_document, source_text, lexical = candidate
            hybrid_score = self.hybrid.score(lexical.combined, semantic_score)
            if hybrid_score < active_threshold:
                continue
            excluded_from_overall = submitted_passage.is_quotation and submitted_passage.has_citation
            matches.append(
                PassageMatch(
                    submitted=normalize_text(submitted_passage.text),
                    source=normalize_text(source_text),
                    source_document=source_document,
                    word_cosine_score=lexical.word_cosine,
                    character_jaccard_score=lexical.character_jaccard,
                    lexical_score=lexical.combined,
                    semantic_score=semantic_score,
                    hybrid_score=hybrid_score,
                    review_band=(
                        "excluded"
                        if excluded_from_overall
                        else review_band(
                            hybrid_score,
                            medium_threshold=medium_review_score,
                            high_threshold=high_review_score,
                        )
                    ),
                    is_quotation=submitted_passage.is_quotation,
                    has_citation=submitted_passage.has_citation,
                    excluded_from_overall=excluded_from_overall,
                )
            )

        matches.sort(key=lambda item: item.hybrid_score, reverse=True)
        excluded_passages = sum(
            passage.is_quotation and passage.has_citation for passage in submitted
        )
        reviewable_passages = len(submitted) - excluded_passages
        included_score = sum(
            match.hybrid_score for match in matches if not match.excluded_from_overall
        )
        overall = included_score / reviewable_passages if reviewable_passages else 0.0
        warnings = [
            "Review bands use pilot validation calibration and must be reconfirmed on the final research dataset.",
            "Similarity is evidence for human review, not a misconduct decision.",
        ]
        if excluded_passages:
            warnings.append(
                f"{excluded_passages} properly cited quotation passage(s) were shown for transparency but excluded from the overall score."
            )
        if self.config.semantic_enabled and not self.semantic.available:
            warnings.append("Semantic mode was requested but its optional package is not installed.")

        return ScanResult(
            submitted_document=document_name,
            model_mode="hybrid" if semantic_active else "lexical baseline",
            total_passages=len(submitted),
            matched_passages=len(matches),
            reviewable_passages=reviewable_passages,
            excluded_passages=excluded_passages,
            overall_score=round(overall, 4),
            review_thresholds={
                "detection": active_threshold,
                "medium": medium_review_score,
                "high": high_review_score,
            },
            matches=matches,
            warnings=warnings,
        )
