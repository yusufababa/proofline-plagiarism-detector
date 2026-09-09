import unittest

from app.models import HybridSimilarityModel, LexicalSimilarityModel, review_band


class SimilarityTests(unittest.TestCase):
    def setUp(self):
        self.model = LexicalSimilarityModel()

    def test_identical_text_has_full_score(self):
        text = "Academic integrity requires proper acknowledgement of source materials."
        score = self.model.score(text, text)
        self.assertEqual(score.word_cosine, 1.0)
        self.assertEqual(score.character_jaccard, 1.0)
        self.assertEqual(score.combined, 1.0)

    def test_unrelated_text_has_low_score(self):
        left = "Academic integrity requires proper acknowledgement of source materials."
        right = "The rainfall forecast predicts thunderstorms near the coast tomorrow."
        self.assertLess(self.model.score(left, right).combined, 0.2)

    def test_hybrid_falls_back_to_lexical(self):
        model = HybridSimilarityModel(lexical_weight=0.55, semantic_weight=0.45)
        self.assertEqual(model.score(0.64, None), 0.64)

    def test_review_bands_are_explicit(self):
        self.assertEqual(review_band(0.8), "high")
        self.assertEqual(review_band(0.6), "medium")
        self.assertEqual(review_band(0.2), "low")


if __name__ == "__main__":
    unittest.main()
