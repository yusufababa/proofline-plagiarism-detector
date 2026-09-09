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

    def test_environment_can_enable_semantic_mode(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ,
            {"SEMANTIC_ENABLED": "true", "MINIMUM_MATCH_SCORE": "0.42"},
        ):
            config = Settings.from_environment(Path(directory))
        self.assertTrue(config.semantic_enabled)
        self.assertEqual(config.minimum_match_score, 0.42)


if __name__ == "__main__":
    unittest.main()

