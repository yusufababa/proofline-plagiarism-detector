# Final Research Dataset Plan

## Selected benchmark

The selected external benchmark is the **PAN Plagiarism Corpus 2011 (PAN-PC-11)**, DOI [10.5281/zenodo.3250095](https://doi.org/10.5281/zenodo.3250095).

The official Zenodo record describes PAN-PC-11 as an evaluation corpus for automatic plagiarism detection that includes both automatically inserted and manually produced plagiarism. It states that the corpus may be used free of charge for research. The archive contains two RAR files totalling approximately 1.7 GB. The [Webis data catalogue](https://webis.de/data.html) reports approximately 2 GB and 27,000 documents.

PAN-PC-11 is treated as research-only material. The raw documents must not be committed to this repository or placed inside downloadable project packages. Only derived identifiers, measurements, and aggregate results may be retained here.

## Why it fits the project

- It was created specifically to evaluate plagiarism-detection systems.
- It contains direct reuse and multiple paraphrase/obfuscation levels.
- It provides source and suspicious-document relationships for ground truth.
- It is widely recognized in plagiarism-detection research.
- Its source-group annotations support leakage-safe splitting.

## Laptop-safe subset protocol

The full corpus is too large for routine work on a 4 GB laptop. The dissertation experiment will therefore use a deterministic English-to-English subset:

1. Download and verify both official archive files on a machine with sufficient storage.
2. Extract only external-detection cases whose suspicious and source passages are English.
3. Group every case by source document before sampling or splitting.
4. Select 300 positive cases: 100 direct/no-obfuscation, 100 low paraphrase, and 100 high or human paraphrase cases.
5. Create 300 topic-matched negative pairs without known plagiarism links.
6. Split source groups 60% training, 20% validation, and 20% test using seed `20260920`.
7. Freeze the test identifiers before model fitting or threshold adjustment.
8. Store raw text under `data/pan_pc_11/`, which is ignored by Git.
9. Export only case identifiers, feature values, labels, aggregate statistics, and error categories.

The 600-case target is a resource-aware dissertation subset, not a replacement for full-corpus benchmarking. Its limitation must be stated in the final report.

## Import command

After extracting the official archive, import a category-balanced positive subset with:

```powershell
.\.venv\Scripts\python.exe -m evaluation.pan_adapter `
  "D:\datasets\pan-plagiarism-corpus-2011\external-detection-corpus" `
  --output "data\pan_pc_11\positive_cases.json" `
  --limit 300
```

The adapter reads PAN offsets and lengths, verifies passage boundaries, filters to English metadata, labels obfuscation categories, and assigns source-grouped splits using seed `20260920`. The imported manifest retains the extracted passage text locally under the ignored `data/` directory and must not be committed or redistributed.

## Citation

Potthast, M., Stein, B., Eiselt, A., Barrón-Cedeño, A., and Rosso, P. (2011). *PAN Plagiarism Corpus 2011 (PAN-PC-11)*. Zenodo. https://doi.org/10.5281/zenodo.3250095
