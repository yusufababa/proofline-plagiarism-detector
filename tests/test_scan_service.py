import tempfile
import unittest
from pathlib import Path

from app.core.config import Settings
from app.repositories import CorpusRepository
from app.services.scanner import ScanService


class ScanServiceTests(unittest.TestCase):
    def test_scan_returns_traceable_match(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Settings(project_root=Path(directory))
            config.prepare_directories()
            content = b"Academic integrity requires proper acknowledgement of all source materials."
            stored_name = "abc_reference.txt"
            (config.reference_dir / stored_name).write_bytes(content)
            repository = CorpusRepository(config.database_path, config.reference_dir)
            repository.initialize()
            repository.add("reference.txt", stored_name, content)
            scanner = ScanService(config, repository)

            result = scanner.scan_text("submission.txt", content.decode())

        self.assertEqual(result.model_mode, "lexical baseline")
        self.assertEqual(result.total_passages, 1)
        self.assertEqual(result.matched_passages, 1)
        self.assertEqual(result.matches[0].source_document, "reference.txt")
        self.assertEqual(result.matches[0].lexical_score, 1.0)
        self.assertEqual(
            result.review_thresholds,
            {"detection": 0.15, "medium": 0.25, "high": 0.69},
        )
        self.assertEqual(result.matches[0].review_band, "high")

    def test_cited_quotation_is_reported_but_excluded_from_overall(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Settings(project_root=Path(directory))
            config.prepare_directories()
            reference_text = (
                "Academic integrity requires proper acknowledgement of every source used in written work. "
                "Independent analysis demonstrates the student's own understanding of the subject."
            )
            content = reference_text.encode()
            stored_name = "reference.txt"
            (config.reference_dir / stored_name).write_bytes(content)
            repository = CorpusRepository(config.database_path, config.reference_dir)
            repository.initialize()
            repository.add("reference.txt", stored_name, content)
            scanner = ScanService(config, repository)
            submission = (
                '"Academic integrity requires proper acknowledgement of every source used in written work" (Smith, 2024). '
                "Independent analysis demonstrates the student's own understanding of the subject."
            )

            result = scanner.scan_text("submission.txt", submission)

        self.assertEqual(result.total_passages, 2)
        self.assertEqual(result.reviewable_passages, 1)
        self.assertEqual(result.excluded_passages, 1)
        self.assertEqual(result.matched_passages, 2)
        excluded = next(match for match in result.matches if match.excluded_from_overall)
        self.assertEqual(excluded.review_band, "excluded")
        self.assertTrue(excluded.is_quotation)
        self.assertTrue(excluded.has_citation)
        self.assertEqual(result.overall_score, 1.0)

    def test_semantic_mode_can_recover_low_lexical_paraphrase(self):
        class SemanticStub:
            available = True

            def score_many(self, pairs):
                return [0.9 for _ in pairs]

        with tempfile.TemporaryDirectory() as directory:
            config = Settings(
                project_root=Path(directory),
                semantic_enabled=True,
                minimum_match_score=0.35,
            )
            config.prepare_directories()
            source = "Businesses rent computing power when needed instead of owning every server."
            submission = "Companies obtain processing capacity on demand without buying all hardware."
            content = source.encode()
            stored_name = "reference.txt"
            (config.reference_dir / stored_name).write_bytes(content)
            repository = CorpusRepository(config.database_path, config.reference_dir)
            repository.initialize()
            repository.add("reference.txt", stored_name, content)
            scanner = ScanService(config, repository)
            scanner.semantic = SemanticStub()

            result = scanner.scan_text("submission.txt", submission)

        self.assertEqual(result.model_mode, "hybrid")
        self.assertEqual(result.matched_passages, 1)
        self.assertLess(result.matches[0].lexical_score, config.minimum_match_score)
        self.assertEqual(result.matches[0].semantic_score, 0.9)
        self.assertGreaterEqual(result.matches[0].hybrid_score, config.minimum_match_score)
        self.assertEqual(
            result.review_thresholds,
            {"detection": 0.20, "medium": 0.46, "high": 0.80},
        )


if __name__ == "__main__":
    unittest.main()
