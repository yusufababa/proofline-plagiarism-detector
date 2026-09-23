import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from docx import Document

from app.domain import PassageMatch, ScanResult
from app.repositories import ScanRepository
from app.services.report_writer import build_evidence_report


def sample_result() -> ScanResult:
    return ScanResult(
        submitted_document="student-submission.docx",
        model_mode="hybrid",
        total_passages=2,
        matched_passages=1,
        reviewable_passages=2,
        excluded_passages=0,
        overall_score=0.42,
        review_thresholds={"detection": 0.20, "medium": 0.46, "high": 0.80},
        matches=[
            PassageMatch(
                submitted="Cloud services provide computing resources on demand.",
                source="Computing resources are supplied on demand by cloud services.",
                source_document="cloud-reference.docx",
                word_cosine_score=0.71,
                character_jaccard_score=0.48,
                lexical_score=0.62,
                semantic_score=0.88,
                hybrid_score=0.74,
                review_band="high",
            )
        ],
        warnings=["Similarity is evidence for human review, not a misconduct decision."],
    )


class ScanHistoryTests(unittest.TestCase):
    def test_save_list_and_retrieve_scan_result(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = ScanRepository(Path(directory) / "test.db")
            repository.initialize()

            record = repository.save(sample_result())
            recent = repository.list_recent()
            restored = repository.get_result(record.id)

        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].submitted_document, "student-submission.docx")
        self.assertEqual(recent[0].overall_score, 0.42)
        self.assertEqual(restored["scan_id"], record.id)
        self.assertEqual(restored["matches"][0]["source_document"], "cloud-reference.docx")
        self.assertEqual(restored["report_url"], f"/api/scans/{record.id}/report")

    def test_missing_scan_returns_none(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = ScanRepository(Path(directory) / "test.db")
            repository.initialize()

            restored = repository.get_result("not-a-real-scan")

        self.assertIsNone(restored)

    def test_delete_removes_only_the_selected_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = ScanRepository(Path(directory) / "test.db")
            repository.initialize()
            first = repository.save(sample_result())
            second = repository.save(sample_result())

            deleted = repository.delete(first.id)

            self.assertTrue(deleted)
            self.assertIsNone(repository.get_result(first.id))
            self.assertIsNotNone(repository.get_result(second.id))
            self.assertFalse(repository.delete("missing"))

    def test_clear_removes_all_saved_scans(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = ScanRepository(Path(directory) / "test.db")
            repository.initialize()
            repository.save(sample_result())
            repository.save(sample_result())

            deleted = repository.clear()

            self.assertEqual(deleted, 2)
            self.assertEqual(repository.list_recent(), [])

    def test_word_report_contains_summary_and_evidence(self):
        payload = sample_result().to_dict()
        payload.update({"scan_id": "abc123", "created_at": "2026-09-20T12:00:00+00:00"})

        report_bytes = build_evidence_report(payload)
        document = Document(BytesIO(report_bytes))
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        table_text = "\n".join(
            cell.text for table in document.tables for row in table.rows for cell in row.cells
        )

        self.assertTrue(report_bytes.startswith(b"PK"))
        self.assertIn("Proofline Similarity Evidence Report", text)
        self.assertIn("human reviewer", text)
        self.assertIn("student-submission.docx", table_text)
        self.assertIn("cloud-reference.docx", text)
        self.assertIn("74.0%", table_text)
        self.assertIn("medium >= 46.0%", table_text)


if __name__ == "__main__":
    unittest.main()
