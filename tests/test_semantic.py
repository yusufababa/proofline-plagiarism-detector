import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.models import SemanticSimilarityModel


class SemanticSimilarityTests(unittest.TestCase):
    def test_availability_check_does_not_load_the_model(self):
        model = SemanticSimilarityModel("example/model")
        with patch("app.models.semantic.find_spec", return_value=object()) as lookup:
            self.assertTrue(model.available)
        lookup.assert_called_once_with("sentence_transformers")
        self.assertIsNone(model._model)

    def test_missing_package_is_reported_as_unavailable(self):
        model = SemanticSimilarityModel("example/model")
        with patch("app.models.semantic.find_spec", return_value=None):
            self.assertFalse(model.available)

    def test_cached_snapshot_enables_offline_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            snapshot = cache / "models--example--model" / "snapshots" / "revision"
            snapshot.mkdir(parents=True)
            (snapshot / "config.json").write_text("{}", encoding="utf-8")
            model = SemanticSimilarityModel("example/model", cache_folder=cache)

            self.assertTrue(model._has_cached_snapshot())


if __name__ == "__main__":
    unittest.main()
