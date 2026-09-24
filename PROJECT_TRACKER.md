# Project Build Tracker

Last updated: 2026-09-20
Current software version: 0.13.0 release candidate
Engineering completion: 97%
Current stage: Release candidate - branded welcome composer and results dashboard complete

> The completion percentage measures implementation progress, not model accuracy.

## 1. Project objectives and measurable deliverables

### Objective 1: preprocessing and similarity algorithms - 100%

Build and verify the components that transform academic documents into comparable passages and calculate lexical and semantic similarity.

- [x] Establish the layered project structure.
- [x] Read TXT documents.
- [x] Read DOCX paragraphs and tables.
- [x] Read text-based PDF pages.
- [x] Normalize Unicode, punctuation, casing, and whitespace.
- [x] Tokenize English text.
- [x] Split documents into reviewable passages.
- [x] Implement word-vector cosine similarity.
- [x] Implement character 4-gram Jaccard similarity.
- [x] Combine lexical components transparently.
- [x] Create a lazy-loaded semantic-model interface.
- [x] Install the optional semantic package in the project environment.
- [x] Validate semantic matching with paraphrased examples.
- [x] Add bibliography-section detection.
- [x] Add quotation and citation identification.
- [x] Add initial boilerplate handling.

Required dissertation evidence:

- Preprocessing input/output examples.
- Mathematical definitions for cosine and Jaccard similarity.
- Justification for passage segmentation and minimum length.
- Unit-test results.
- Direct-copy, edited-copy, paraphrase, and unrelated examples.

### Objective 2: intelligent decision-support integration - 100%

Combine complementary evidence into a transparent system that assists a human reviewer.

- [x] Separate lexical, semantic, and hybrid model implementations.
- [x] Add a transparent weighted hybrid baseline.
- [x] Expose component scores in the scan response.
- [x] Display the submitted and source passages side by side.
- [x] Identify the matching source document.
- [x] State that results require human interpretation.
- [x] Build a labelled pilot feature dataset.
- [x] Compare lexical, semantic, and weighted-hybrid pilot results.
- [x] Train a pilot logistic-regression fusion model using the training split only.
- [x] Compare learned fusion with the weighted baseline on the untouched test split.
- [x] Calibrate low, medium, and high review-risk bands.
- [x] Add saved scan history.
- [x] Add a downloadable evidence report.

Required dissertation evidence:

- Architecture diagram and data flow.
- Feature table with word, character, semantic, and coverage signals.
- Baseline weights and learned coefficients.
- Threshold-selection procedure.
- Screenshots of explainable passage matches.

### Objective 3: quantitative evaluation - 93%

Measure whether the proposed hybrid approach improves on individual algorithms.

- [x] Select PAN-PC-11 and document its DOI, research-use terms, size, and subset protocol.
- [x] Define pilot passage-level ground truth.
- [x] Create source-grouped, leakage-safe training, validation, and test splits.
- [x] Keep the test split out of threshold selection.
- [x] Implement precision, recall, and F1-score calculations.
- [x] Measure false-positive rate.
- [x] Measure processing time and traced Python peak memory use.
- [x] Evaluate the lexical-only model on the synthetic pilot.
- [x] Evaluate the semantic-only model on the synthetic pilot.
- [x] Evaluate the weighted hybrid model on the synthetic pilot.
- [x] Evaluate logistic-regression fusion on the synthetic pilot.
- [x] Perform pilot category-level error analysis.
- [ ] Produce final tables and charts.

Required dissertation evidence:

- Reproducible experiment command.
- Dataset and split statistics.
- Confusion matrices and metric tables.
- Runtime and memory comparison.
- Error categories and representative examples.

## 2. Software modules

| Layer | Source code | Status | Purpose |
|---|---|---:|---|
| Startup | `app/main.py` | Complete | Creates the application and wires dependencies |
| API | `app/api/routes.py` | Enhanced complete | Exposes health, progress, corpus, scanning, history, detail, and report endpoints |
| Configuration | `app/core/config.py` | Complete | Centralizes limits, paths, model weights, and environment settings |
| Domain | `app/domain/entities.py` | Complete | Defines passages, scores, corpus records, matches, and results |
| Lexical model | `app/models/lexical.py` | Baseline complete | Calculates word cosine and character n-gram similarity |
| Semantic model | `app/models/semantic.py` | Interface complete | Lazily calculates embedding cosine similarity when enabled |
| Hybrid model | `app/models/hybrid.py` | Pilot calibrated | Combines model scores and assigns configurable validation-calibrated review bands |
| Learned fusion | `app/models/fusion_classifier.py` | Pilot complete | Fits explainable logistic-regression coefficients without a runtime ML dependency |
| Corpus repository | `app/repositories/corpus.py` | Initial complete | Catalogues sources in SQLite and detects duplicates by hash |
| Scan repository | `app/repositories/scans.py` | Complete | Persists scan summaries and explainable result payloads in SQLite |
| Extraction | `app/services/document_extractor.py` | Initial complete | Extracts text from supported document types |
| Preprocessing | `app/services/preprocessing.py` | Academic baseline complete | Normalizes and segments text, removes bibliography content and boilerplate, and identifies citations and quotations |
| File storage | `app/services/file_storage.py` | Complete | Validates file names and creates collision-safe storage names |
| Scan service | `app/services/scanner.py` | Baseline complete | Coordinates the end-to-end detection pipeline |
| Report writer | `app/services/report_writer.py` | Complete | Generates downloadable Microsoft Word evidence reports on demand |
| Web interface | `app/web/` | Enhanced prototype complete | Provides responsive drag-and-drop queues, live upload progress, corpus details, and explainable evidence |
| Evaluation | `evaluation/` | Analysis pilot complete | Trains models, calculates category errors, exports features, and generates SVG charts |
| PAN adapter | `evaluation/pan_adapter.py` | Complete pending real archive | Imports PAN offsets, validates passages, balances categories, and prevents source leakage |
| Band calibration | `evaluation/calibration.py` | Pilot complete | Derives lexical and hybrid priority boundaries from validation categories without test leakage |
| Test suite | `tests/` | Active | Protects preprocessing, models, storage, and scanning behaviour |

For detailed ownership and extension points, read `docs/SOURCE_CODE_GUIDE.md`.

## 3. Product milestones

### Milestone A - foundation

- [x] Project layout and naming.
- [x] Central configuration.
- [x] Environment template.
- [x] Setup, run, and test commands.
- [x] Architecture and API documentation.

### Milestone B - corpus and lexical prototype

- [x] Reference upload.
- [x] Duplicate detection.
- [x] SQLite reference catalogue.
- [x] Submitted-document upload.
- [x] Lexical passage matching.
- [x] Explainable component scores.
- [x] Responsive drag-and-drop upload workflow and progress states.
- [x] Branded pasted-text and file-upload welcome composer.
- [x] Results dashboard with overview, evidence, history, source-library, and project navigation.
- [x] Citation and quotation evidence flags.
- [x] Bibliography and simple boilerplate filtering.
- [x] Automated Edge DOM smoke check for the final interface controls.
- [ ] Test the complete browser workflow after dependency installation.

### Milestone C - semantic and hybrid prototype

- [x] Low-memory semantic interface.
- [x] Best-candidate-only semantic design.
- [x] Install and benchmark the semantic model.
- [x] Complete pilot paraphrase test cases.
- [x] Train and compare a pilot learned fusion rule.

### Milestone D - evaluation

- [x] Synthetic pilot dataset preparation.
- [x] Reproducible experiment runner.
- [x] Metric calculation.
- [x] JSON and Markdown results export.
- [x] Pilot metric and category-analysis SVG charts.
- [ ] Final charts from the research dataset.
- [x] Pilot category-level error analysis.
- [x] PAN-PC-11 text/XML import adapter with deterministic subset selection.

### Milestone E - final product

- [x] Saved scan records.
- [x] Downloadable similarity report.
- [x] Local scan-history privacy and deletion controls.
- [x] Confirm authentication is out of scope for the local single-user release and required before any future multi-user deployment.
- [x] Automated keyboard and accessibility checks.
- [ ] Manual cross-browser visual and workflow testing.
- [x] Demonstration corpus.
- [ ] Installation verification on a clean Windows account.

## 4. Verification record

| Date | Verification | Result |
|---|---|---|
| 2026-09-03 | Original preprocessing and similarity tests | 7 passed |
| 2026-09-03 | Python and JavaScript syntax | Passed |
| 2026-09-03 | Reorganized unit and service tests | 11 passed |
| 2026-09-03 | Python and JavaScript syntax after reorganization | Passed |
| 2026-09-08 | Enhanced interface: desktop/mobile render and JavaScript syntax | Passed |
| 2026-09-08 | Regression test after interface enhancement | 11 passed |
| 2026-09-20 | Academic-text handling and cited-quotation exclusion tests | 16 passed |
| 2026-09-20 | Python compilation and JavaScript syntax | Passed |
| 2026-09-20 | Isolated live API upload and citation-aware scan | Passed on version 0.3.0 |
| 2026-09-20 | Pilot dataset, evaluation metrics, cache, and memory checks | 24 tests passed |
| 2026-09-20 | Lexical pilot on untouched synthetic test split | Precision 1.00, recall 0.67, F1 0.80 after exclusions |
| 2026-09-20 | MiniLM CPU installation and project-local cache | Sentence Transformers 6.1.0; model cache 87.34 MB |
| 2026-09-20 | Cached semantic/hybrid pilot on untouched test split | Semantic F1 0.91; hybrid F1 1.00; peak process memory 503.36 MB |
| 2026-09-20 | End-to-end semantic scan through `ScanService` | Low-lexical paraphrase recovered at hybrid score 0.2026 |
| 2026-09-20 | Logistic regression and non-blocking semantic availability checks | 28 tests passed |
| 2026-09-20 | Learned fusion versus weighted hybrid on untouched pilot test | Both reached F1 1.00; learned fusion did not improve the baseline |
| 2026-09-20 | PAN-PC-11 dataset decision | DOI, research-use restriction, 1.7 GB archive, and 600-case subset protocol documented |
| 2026-09-20 | Category analysis and SVG chart generation | 29 tests passed; both charts visually verified |
| 2026-09-20 | PAN adapter fixture and CLI verification | 33 tests passed; direct copy and paraphrase offsets imported correctly |
| 2026-09-20 | SQLite history persistence and Word-report validation | 37 tests passed; live API saved the demo scan and its generated DOCX reopened successfully |
| 2026-09-20 | Validation-only review-band calibration | 40 tests passed; lexical bands 0.25/0.69 and hybrid bands 0.46/0.80; untouched hybrid pilot test F1 1.00 |
| 2026-09-20 | Local privacy controls and accessibility regression | 46 tests passed; individual and clear-all deletion verified in isolated API tests |
| 2026-09-20 | Graphical browser automation | Browser surface unavailable in the current session; manual cross-browser visual check remains open |
| 2026-09-20 | Edge DOM smoke check | Local interface rendered and final history and privacy controls were present |
| 2026-09-20 | Final technical report layout | Eight pages rendered and inspected; pagination defect corrected before delivery |
| 2026-09-20 | Version 0.12.0 release verifier | 46 tests, 40 Python syntax files, JavaScript syntax, version metadata, DOCX package, and live health all passed |
| 2026-09-21 | Complete UI/UX revamp | Satoshi-led welcome composer and responsive dashboard rendered in Edge at desktop and tablet widths; 47 tests passed |
| 2026-09-21 | Permission-safe submission storage | Scans now use auto-deleted system temporary storage; live DOCX scan returned 5 hybrid matches and all 48 tests passed |

## 5. Immediate next actions

1. Test the complete upload, scan, history, deletion, and report workflow manually in Chrome and Edge.
2. Verify installation on a clean Windows account.
3. Download PAN-PC-11 on a machine with at least 5 GB free storage.
4. Run the adapter and independently review the planned 600-case evaluation subset.
5. Retrain, recalibrate, and compare all models on the expanded dataset.
6. Produce final research-dataset charts and dissertation tables.

## 6. Definition of done

The project is complete when a new installation can:

1. Load a documented, lawful reference corpus.
2. Scan an unseen English academic document.
3. Show traceable passage-level evidence and component scores.
4. Treat quotations, references, and boilerplate appropriately.
5. Reproduce the lexical, semantic, and hybrid evaluation from one documented command.
6. Produce the same final metrics reported in the dissertation.
