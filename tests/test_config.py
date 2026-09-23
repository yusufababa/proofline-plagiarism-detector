import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.config import Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_are_low_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Settings.from_environment(Path(directory))
        self.assertFalse(config.semantic_enabled)
        self.assertEqual(config.max_upload_mb, 10)
        self.assertEqual(config.semantic_minimum_match_score, 0.20)
        self.assertEqual(config.minimum_match_score, 0.15)
        self.assertEqual(config.lexical_medium_review_score, 0.25)
        self.assertEqual(config.lexical_high_review_score, 0.69)
        self.assertEqual(config.hybrid_medium_review_score, 0.46)
        self.assertEqual(config.hybrid_high_review_score, 0.80)
        self.assertEqual(config.semantic_cache_dir, Path(directory) / "data" / "models")

    def test_review_thresholds_must_be_ordered(self):
        config = Settings(
            project_root=Path("."),
            hybrid_medium_review_score=0.90,
            hybrid_high_review_score=0.80,
        )
        with self.assertRaises(ValueError):
            config.validate()

    def test_environment_can_enable_semantic_mode(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ,
            {"SEMANTIC_ENABLED": "true", "MINIMUM_MATCH_SCORE": "0.42"},
        ):
            config = Settings.from_environment(Path(directory))
        self.assertTrue(config.semantic_enabled)
        self.assertEqual(config.minimum_match_score, 0.42)

    def test_environment_can_override_semantic_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "model-cache"
            with patch.dict(os.environ, {"SEMANTIC_CACHE_DIR": str(cache_path)}):
                config = Settings.from_environment(Path(directory))
                self.assertEqual(config.semantic_cache_dir, cache_path)


if __name__ == "__main__":
    unittest.main()
