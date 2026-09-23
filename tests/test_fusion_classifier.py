import unittest

from app.models import LogisticRegressionFusionModel


class LogisticRegressionFusionTests(unittest.TestCase):
    def test_model_learns_separable_similarity_features(self):
        features = [
            [0.95, 0.90, 0.96],
            [0.75, 0.70, 0.85],
            [0.10, 0.05, 0.12],
            [0.20, 0.15, 0.18],
        ]
        model = LogisticRegressionFusionModel(epochs=1000)
        model.fit(features, [1, 1, 0, 0])

        self.assertGreater(model.score([0.85, 0.80, 0.90]), 0.5)
        self.assertLess(model.score([0.12, 0.10, 0.15]), 0.5)
        self.assertEqual(len(model.parameters(["word", "character", "semantic"])["coefficients"]), 3)

    def test_model_requires_both_training_classes(self):
        model = LogisticRegressionFusionModel()
        with self.assertRaises(ValueError):
            model.fit([[0.5], [0.7]], [1, 1])


if __name__ == "__main__":
    unittest.main()

