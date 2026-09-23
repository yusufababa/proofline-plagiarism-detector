# Evaluation workflow

This folder contains the reproducible pilot evaluation for Proofline.

The bundled dataset is synthetic and released under CC0-1.0. It is deliberately grouped by source so that variants from one source never appear in more than one split. The test split must remain untouched while thresholds are selected from the validation split.

Run the lightweight lexical experiment:

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner
```

Results are written to `reports/evaluation_results.json` and `reports/evaluation_results.md`.
Each model result also contains review-band boundaries derived only from validation examples. The deployed pilot values and method are documented in `CALIBRATION_RESULTS.md` and `calibrated_review_bands.json`.

After installing the optional semantic dependencies, compare lexical, MiniLM semantic, and weighted-hybrid models:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt
.\.venv\Scripts\python.exe -m evaluation.runner --semantic
```

On a 4 GB laptop, close other applications before the semantic run. The base lexical experiment remains the safe default.

If Windows reports that `data/models` is not writable, set `SEMANTIC_CACHE_DIR` in `.env` to a writable local folder before running the benchmark.

This pilot proves that the experiment pipeline works. A larger, externally documented dataset is still required before reporting final dissertation performance claims.
