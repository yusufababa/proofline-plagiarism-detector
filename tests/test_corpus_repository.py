import tempfile
import unittest
from pathlib import Path

from app.repositories import CorpusRepository


class CorpusRepositoryTests(unittest.TestCase):
    def test_add_and_list_reference_document(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference_dir = root / "reference"
            reference_dir.mkdir()
            repository = CorpusRepository(root / "test.db", reference_dir)
            repository.initialize()
            document = repository.add("source.txt", "abc_source.txt", b"source content")

            records = repository.list_all()

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, document.id)
        self.assertEqual(records[0].original_name, "source.txt")


if __name__ == "__main__":
    unittest.main()

