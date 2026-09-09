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


if __name__ == "__main__":
    unittest.main()

