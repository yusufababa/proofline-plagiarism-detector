# Proofline Learned-Fusion Pilot Results

Version 0.6.0 adds a dependency-free logistic-regression fusion model and compares it with the fixed 55% lexical / 45% semantic weighted baseline.

The classifier was fitted only on the 10 training examples. Validation data selected the decision threshold, and the 10 test examples remained untouched until final measurement.

## Learned model

- Features: word cosine, character 4-gram Jaccard, and MiniLM semantic similarity.
- Training target: raw similarity label.
- Training examples: 10.
- Validation-selected review threshold: 0.75.
- Standardized coefficients: word `0.209869`, character `-0.080454`, semantic `3.267258`.
- Intercept: `3.001661`.
- Training method: balanced logistic loss, L2 regularization, and deterministic gradient descent.

The much larger semantic coefficient means MiniLM contributed most strongly to this tiny pilot model. The slightly negative character coefficient should not be interpreted as proof that character overlap is harmful; correlated features and only ten training examples make individual coefficients unstable.

## Untouched pilot test comparison

| Model | Precision | Recall | F1 | Accuracy | False-positive rate |
|---|---:|---:|---:|---:|---:|
| Weighted hybrid | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Learned logistic fusion | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Learned fusion matched the weighted baseline; it did not outperform it. This validates the training and comparison pipeline, but the pilot dataset is far too small to decide which fusion method generalizes better.

## Research conclusion

The learned model must remain evaluation-only until a larger, independently reviewed dataset is available. The application therefore continues using the transparent weighted hybrid. This prevents unstable pilot coefficients from silently affecting student-document results.

Reproduce all four models with:

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner --semantic
```

