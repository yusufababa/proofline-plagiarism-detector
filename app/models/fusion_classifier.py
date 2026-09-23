from __future__ import annotations

import math


class LogisticRegressionFusionModel:
    """Small dependency-free logistic model for combining similarity features."""

    name = "learned_fusion"

    def __init__(
        self,
        learning_rate: float = 0.1,
        epochs: int = 2000,
        l2_strength: float = 0.01,
    ) -> None:
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2_strength = l2_strength
        self.means: list[float] = []
        self.scales: list[float] = []
        self.coefficients: list[float] = []
        self.intercept = 0.0
        self.is_fitted = False

    @staticmethod
    def _sigmoid(value: float) -> float:
        if value >= 0:
            return 1.0 / (1.0 + math.exp(-value))
        exponential = math.exp(value)
        return exponential / (1.0 + exponential)

    def _standardize(self, features: list[float]) -> list[float]:
        return [
            (value - mean) / scale
            for value, mean, scale in zip(features, self.means, self.scales, strict=True)
        ]

    def fit(self, features: list[list[float]], labels: list[int]) -> None:
        if not features or len(features) != len(labels):
            raise ValueError("Features and labels must contain the same non-zero number of rows.")
        width = len(features[0])
        if width == 0 or any(len(row) != width for row in features):
            raise ValueError("Every feature row must have the same non-zero width.")
        if set(labels) != {0, 1}:
            raise ValueError("Training labels must contain both class 0 and class 1.")

        self.means = [sum(row[index] for row in features) / len(features) for index in range(width)]
        self.scales = []
        for index, mean in enumerate(self.means):
            variance = sum((row[index] - mean) ** 2 for row in features) / len(features)
            self.scales.append(math.sqrt(variance) or 1.0)

        standardized = [self._standardize(row) for row in features]
        self.coefficients = [0.0] * width
        self.intercept = 0.0
        positive_count = sum(labels)
        negative_count = len(labels) - positive_count
        class_weights = {
            0: len(labels) / (2 * negative_count),
            1: len(labels) / (2 * positive_count),
        }

        for _ in range(self.epochs):
            coefficient_gradients = [0.0] * width
            intercept_gradient = 0.0
            for row, label in zip(standardized, labels, strict=True):
                linear = self.intercept + sum(
                    coefficient * value
                    for coefficient, value in zip(self.coefficients, row, strict=True)
                )
                error = (self._sigmoid(linear) - label) * class_weights[label]
                intercept_gradient += error
                for index, value in enumerate(row):
                    coefficient_gradients[index] += error * value

            row_count = len(features)
            self.intercept -= self.learning_rate * (intercept_gradient / row_count)
            for index in range(width):
                gradient = coefficient_gradients[index] / row_count
                gradient += self.l2_strength * self.coefficients[index]
                self.coefficients[index] -= self.learning_rate * gradient

        self.is_fitted = True

    def score(self, features: list[float]) -> float:
        if not self.is_fitted:
            raise RuntimeError("Fit the logistic-regression fusion model before scoring.")
        if len(features) != len(self.coefficients):
            raise ValueError("Feature width does not match the fitted model.")
        standardized = self._standardize(features)
        linear = self.intercept + sum(
            coefficient * value
            for coefficient, value in zip(self.coefficients, standardized, strict=True)
        )
        return round(self._sigmoid(linear), 4)

    def parameters(self, feature_names: list[str]) -> dict[str, object]:
        if not self.is_fitted:
            raise RuntimeError("Fit the logistic-regression fusion model before exporting parameters.")
        if len(feature_names) != len(self.coefficients):
            raise ValueError("Feature names must match the fitted feature width.")
        return {
            "feature_names": feature_names,
            "means": [round(value, 6) for value in self.means],
            "scales": [round(value, 6) for value in self.scales],
            "coefficients": [round(value, 6) for value in self.coefficients],
            "intercept": round(self.intercept, 6),
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "l2_strength": self.l2_strength,
        }

