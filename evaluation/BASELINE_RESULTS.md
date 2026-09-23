# Proofline Lexical Pilot Results

The v0.4.0 experiment used 30 original synthetic examples across six source groups. Each source and all of its variants belong to only one split, preventing the same source from leaking between training, validation, and test data.

This pilot validates the evaluation method. It is not a substitute for the larger, documented research dataset required for final dissertation claims.

## Experiment summary

- Categories: direct copy, light edit, paraphrase, cited quotation, and unrelated text.
- Split sizes: 10 train, 10 validation, and 10 untouched test examples.
- Threshold: 0.15, selected using only the validation split.
- Test precision after citation/quotation exclusions: 1.0000.
- Test recall after citation/quotation exclusions: 0.6667.
- Test F1 after citation/quotation exclusions: 0.8000.
- Test accuracy after citation/quotation exclusions: 0.8000.
- Test false-positive rate: 0.0000.
- Pilot runtime: approximately 0.05 seconds.
- Traced Python peak memory: approximately 0.07 MB.

## Interpretation

The lexical model correctly avoided false positives in this small pilot and detected direct or lightly edited overlap. Its lower recall came from paraphrase examples that share meaning but use substantially different words. This is the expected limitation and provides a measurable reason to evaluate MiniLM next.

Correctly cited quotations remain positive examples for raw textual similarity, because they genuinely reproduce source wording. The end-to-end review evaluation then applies the quotation-and-citation rule and excludes them from the review decision.

Version 0.10.0 deploys this validation-selected threshold as an explicitly labelled pilot setting. It must still be recalibrated using the final research dataset.

## Reproduce the result

```powershell
.\.venv\Scripts\python.exe -m evaluation.runner
```

The runner exports detailed per-case features and metrics to the `reports` directory.

The completed MiniLM and hybrid comparison is documented in `evaluation/SEMANTIC_RESULTS.md`.
