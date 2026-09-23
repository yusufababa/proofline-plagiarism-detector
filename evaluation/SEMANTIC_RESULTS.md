# Proofline MiniLM and Hybrid Pilot Results

Version 0.5.0 evaluated the lexical baseline, `sentence-transformers/all-MiniLM-L6-v2`, and the transparent 55% lexical / 45% semantic hybrid on the same frozen synthetic pilot split.

This is an engineering benchmark, not final dissertation evidence. The dataset contains only 30 synthetic examples and must be replaced or extended with a larger lawful research dataset before making general performance claims.

## Environment

- Device: CPU only.
- Sentence Transformers: 6.1.0.
- PyTorch: 2.14.0+cpu.
- Transformers: 5.17.0.
- Model cache size: approximately 87.34 MB.
- Complete semantic-enabled virtual environment: approximately 1.02 GB.
- Cached evaluation runtime: approximately 3.96 seconds for 30 passage pairs.
- Peak process memory: approximately 503.36 MB.
- Semantic mode remains disabled by default for normal application startup.

## Untouched test results after citation and quotation exclusions

| Model | Validation threshold | Precision | Recall | F1 | Accuracy | False-positive rate |
|---|---:|---:|---:|---:|---:|---:|
| Lexical | 0.15 | 1.0000 | 0.6667 | 0.8000 | 0.8000 | 0.0000 |
| MiniLM semantic | 0.50 | 1.0000 | 0.8333 | 0.9091 | 0.9000 | 0.0000 |
| Weighted hybrid | 0.20 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

## Interpretation

MiniLM improved test recall from 0.6667 to 0.8333, confirming that semantic embeddings recover some paraphrases missed by word and character overlap. The weighted hybrid combined both signals and classified all ten pilot test examples correctly.

The perfect hybrid pilot result must not be described as the expected accuracy on real student work. The test set is intentionally small and synthetic. The result shows only that the integration works and that the semantic component adds useful evidence under these controlled examples.

The application uses the pilot hybrid detection threshold of 0.20 when semantic mode is enabled. Version 0.10.0 also deploys separately calibrated review bands; see `CALIBRATION_RESULTS.md`. All pilot thresholds remain subject to recalibration on the final research dataset.

The measured peak process memory of about 503 MB indicates that the model can run within a 4 GB laptop's physical memory when other heavy applications are closed. The full virtual environment occupies about 1.02 GB because CPU PyTorch and its scientific dependencies are larger than the MiniLM model itself.

## Reproduce the comparison

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt
.\.venv\Scripts\python.exe -m evaluation.runner --semantic
```

If the default cache location is restricted, set `SEMANTIC_CACHE_DIR` in `.env` to a writable local folder.
