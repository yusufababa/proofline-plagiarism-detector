# Final Release Checklist

This checklist separates completed software engineering from the remaining dissertation research work.

## Release candidate completed

- Application version is `0.12.0`.
- Lexical, semantic, weighted-hybrid, and evaluation-only learned-fusion models are implemented.
- TXT, DOCX, and text-based PDF workflows are implemented.
- Saved history, evidence details, deletion controls, and downloadable Word reports are implemented.
- Accessibility regression checks and an Edge DOM smoke check are complete.
- The lecturer demonstration corpus, student submission, and technical Word report are included.
- Run `.\verify_release.ps1` to check tests, syntax, versions, metadata, and report integrity.

## Manual checks before submission day

- Start the application with `.\run.ps1` and complete one full workflow in Edge and Chrome.
- Add every file in `lecturer_demo\Corpus`, scan `lecturer_demo\Document to Scan\Student Submission Demo.docx`, reopen its history record, and download its report.
- Install and start the project once from a clean Windows account or a second Windows computer.
- Capture final screenshots only after these checks pass.

## Research work that remains

- Obtain the authorised PAN-PC-11 archive separately; it is not redistributed with this project.
- Run the tested PAN adapter and independently review the planned 600-case balanced subset.
- Retrain or compare models using the training split, recalibrate on validation data, and report the untouched test result once.
- Produce the final charts and dissertation tables from that expanded dataset.

The current synthetic pilot proves that the pipeline works. It does not establish general real-world accuracy, so the pilot scores must not be presented as final effectiveness claims.
