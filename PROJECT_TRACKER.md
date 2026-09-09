# Project Build Tracker

Last updated: 2026-09-08  
Current software version: 0.2.0  
Engineering completion: 30%  
Current stage: Objective 1 - lexical baseline validation

> The completion percentage measures implementation progress, not model accuracy.

## 1. Project objectives and measurable deliverables

### Objective 1: preprocessing and similarity algorithms - 70%

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
- [ ] Install the optional semantic package on a suitable machine.
- [ ] Validate semantic matching with paraphrased examples.
- [ ] Add bibliography-section detection.
- [ ] Add quotation and citation identification.
- [ ] Add boilerplate handling.

Required dissertation evidence:

- Preprocessing input/output examples.
- Mathematical definitions for cosine and Jaccard similarity.
- Justification for passage segmentation and minimum length.
- Unit-test results.
- Direct-copy, edited-copy, paraphrase, and unrelated examples.

### Objective 2: intelligent decision-support integration - 25%

Combine complementary evidence into a transparent system that assists a human reviewer.

- [x] Separate lexical, semantic, and hybrid model implementations.
- [x] Add a transparent weighted hybrid baseline.
- [x] Expose component scores in the scan response.
- [x] Display the submitted and source passages side by side.
- [x] Identify the matching source document.
- [x] State that results require human interpretation.
- [ ] Build a labelled feature dataset.
- [ ] Train a logistic-regression fusion model.
- [ ] Compare learned fusion with the weighted baseline.
- [ ] Calibrate low, medium, and high review-risk bands.
- [ ] Add saved scan history.
- [ ] Add a downloadable evidence report.

Required dissertation evidence:

- Architecture diagram and data flow.
- Feature table with word, character, semantic, and coverage signals.
- Baseline weights and learned coefficients.
- Threshold-selection procedure.
- Screenshots of explainable passage matches.

### Objective 3: quantitative evaluation - 0%

Measure whether the proposed hybrid approach improves on individual algorithms.

- [ ] Select the research dataset and document its licence.
- [ ] Define passage-level ground truth.
- [ ] Create leakage-safe training, validation, and test splits.
- [ ] Freeze the untouched test set.
- [ ] Implement precision, recall, and F1-score calculations.
- [ ] Measure false-positive rate.
- [ ] Measure processing time and peak memory use.
- [ ] Evaluate the lexical-only model.
- [ ] Evaluate the semantic-only model.
- [ ] Evaluate the weighted hybrid model.
- [ ] Evaluate logistic-regression fusion.
- [ ] Perform ablation and error analysis.
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
| API | `app/api/routes.py` | Initial complete | Validates uploads and exposes health, progress, corpus, and scan endpoints |
| Configuration | `app/core/config.py` | Complete | Centralizes limits, paths, model weights, and environment settings |
| Domain | `app/domain/entities.py` | Complete | Defines passages, scores, corpus records, matches, and results |
| Lexical model | `app/models/lexical.py` | Baseline complete | Calculates word cosine and character n-gram similarity |
| Semantic model | `app/models/semantic.py` | Interface complete | Lazily calculates embedding cosine similarity when enabled |
| Hybrid model | `app/models/hybrid.py` | Baseline complete | Combines model scores and assigns provisional review bands |
| Corpus repository | `app/repositories/corpus.py` | Initial complete | Catalogues sources in SQLite and detects duplicates by hash |
| Extraction | `app/services/document_extractor.py` | Initial complete | Extracts text from supported document types |
| Preprocessing | `app/services/preprocessing.py` | Initial complete | Normalizes, tokenizes, and segments text |
| File storage | `app/services/file_storage.py` | Complete | Validates file names and creates collision-safe storage names |
| Scan service | `app/services/scanner.py` | Baseline complete | Coordinates the end-to-end detection pipeline |
| Web interface | `app/web/` | Enhanced prototype complete | Provides responsive drag-and-drop queues, live upload progress, corpus details, and explainable evidence |
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
- [ ] Test the complete browser workflow after dependency installation.

### Milestone C - semantic and hybrid prototype

- [x] Low-memory semantic interface.
- [x] Best-candidate-only semantic design.
- [ ] Install and benchmark the semantic model.
- [ ] Complete paraphrase test cases.
- [ ] Calibrate or learn the fusion rule.

### Milestone D - evaluation

- [ ] Dataset preparation.
- [ ] Experiment runner.
- [ ] Metric calculation.
- [ ] Results export and charts.
- [ ] Error analysis.

### Milestone E - final product

- [ ] Saved scan records.
- [ ] Downloadable similarity report.
- [ ] Authentication and privacy controls.
- [ ] Accessibility and browser testing.
- [ ] Demonstration corpus.
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

## 5. Immediate next actions

1. Run `setup.ps1` with a stable internet connection.
2. Run `test.ps1` and record the final number of passing tests above.
3. Start the application with `run.ps1`.
4. Confirm that the existing reference document appears in the corpus list.
5. Add controlled direct-copy, edited-copy, paraphrase, and unrelated test documents.
6. Record the lexical scores and inspect false positives.
7. Only then install and enable the semantic model.

## 6. Definition of done

The project is complete when a new installation can:

1. Load a documented, lawful reference corpus.
2. Scan an unseen English academic document.
3. Show traceable passage-level evidence and component scores.
4. Treat quotations, references, and boilerplate appropriately.
5. Reproduce the lexical, semantic, and hybrid evaluation from one documented command.
6. Produce the same final metrics reported in the dissertation.
