import unittest

from app.services.preprocessing import normalize_text, split_passages, tokenize


class PreprocessingTests(unittest.TestCase):
    def test_normalizes_spacing_and_quotes(self):
        self.assertEqual(normalize_text("  A   student\u2019s  work. "), "A student's work.")

    def test_tokenizes_case_insensitively(self):
        self.assertEqual(tokenize("Text-Similarity, TEXT!"), ["text", "similarity", "text"])

    def test_ignores_tiny_passages(self):
        passages = split_passages("Too short. This sentence contains enough useful words for comparison.")
        self.assertEqual(len(passages), 1)
        self.assertIn("enough useful words", passages[0].text)


if __name__ == "__main__":
    unittest.main()
