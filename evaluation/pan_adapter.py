from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree


ENGLISH_CODES = {"en", "eng", "english"}


@dataclass
class PanCase:
    case_id: str
    suspicious_reference: str
    source_reference: str
    suspicious_offset: int
    suspicious_length: int
    source_offset: int
    source_length: int
    candidate_text: str
    source_text: str
    category: str
    split: str = "unassigned"


def _language(document: ElementTree.Element) -> str | None:
    for element in document.iter():
        for key in ("lang", "language"):
            value = element.attrib.get(key)
            if value:
                return value.strip().lower()
    return None


def _category(feature: ElementTree.Element) -> str:
    manual = feature.attrib.get("manual_obfuscation", "").lower() == "true"
    obfuscation = " ".join(
        feature.attrib.get(key, "").lower()
        for key in ("obfuscation", "type", "translation")
    )
    if "translation" in obfuscation or feature.attrib.get("translation", "").lower() == "true":
        return "translation"
    if manual or "paraphrase" in obfuscation or "high" in obfuscation:
        return "paraphrase"
    if "low" in obfuscation or "random" in obfuscation:
        return "light_edit"
    return "direct_copy"


def _integer_attribute(feature: ElementTree.Element, name: str) -> int:
    value = feature.attrib.get(name)
    if value is None:
        raise ValueError(f"Missing PAN annotation attribute: {name}")
    number = int(value)
    if number < 0:
        raise ValueError(f"PAN annotation attribute {name} cannot be negative.")
    return number


def _slice(text: str, offset: int, length: int, reference: str) -> str:
    end = offset + length
    if end > len(text):
        raise ValueError(
            f"Annotation for {reference} ends at {end}, beyond text length {len(text)}."
        )
    return text[offset:end]


def _file_index(corpus_root: Path, suffix: str) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in corpus_root.rglob(f"*{suffix}"):
        index.setdefault(path.name, path)
    return index


def load_pan_cases(
    corpus_root: Path,
    *,
    english_only: bool = True,
    include_unknown_language: bool = False,
) -> list[PanCase]:
    """Load external-plagiarism cases from PAN text/XML annotations."""

    if not corpus_root.exists():
        raise FileNotFoundError(f"PAN corpus directory does not exist: {corpus_root}")

    text_files = _file_index(corpus_root, ".txt")
    xml_files = list(corpus_root.rglob("*.xml"))
    language_by_reference: dict[str, str | None] = {}
    parsed_documents: list[tuple[Path, ElementTree.Element]] = []

    for xml_path in xml_files:
        document = ElementTree.parse(xml_path).getroot()
        reference = document.attrib.get("reference")
        if reference:
            language_by_reference[reference] = _language(document)
        parsed_documents.append((xml_path, document))

    cases: list[PanCase] = []
    for xml_path, document in parsed_documents:
        suspicious_reference = document.attrib.get("reference", xml_path.with_suffix(".txt").name)
        suspicious_path = text_files.get(suspicious_reference)
        if suspicious_path is None:
            continue
        suspicious_language = language_by_reference.get(suspicious_reference)
        suspicious_text = suspicious_path.read_text(encoding="utf-8", errors="replace")

        plagiarism_features = [
            feature
            for feature in document.iter("feature")
            if feature.attrib.get("name") in {"plagiarism", "detected-plagiarism"}
            and feature.attrib.get("source_reference")
        ]
        for index, feature in enumerate(plagiarism_features, start=1):
            source_reference = feature.attrib["source_reference"]
            source_path = text_files.get(source_reference)
            if source_path is None:
                continue
            source_language = language_by_reference.get(source_reference)
            if english_only:
                languages = (suspicious_language, source_language)
                if any(
                    language not in ENGLISH_CODES
                    for language in languages
                    if language is not None
                ):
                    continue
                if not include_unknown_language and any(language is None for language in languages):
                    continue

            source_text = source_path.read_text(encoding="utf-8", errors="replace")
            suspicious_offset = _integer_attribute(feature, "this_offset")
            suspicious_length = _integer_attribute(feature, "this_length")
            source_offset = _integer_attribute(feature, "source_offset")
            source_length = _integer_attribute(feature, "source_length")
            cases.append(
                PanCase(
                    case_id=f"{Path(suspicious_reference).stem}:{index}",
                    suspicious_reference=suspicious_reference,
                    source_reference=source_reference,
                    suspicious_offset=suspicious_offset,
                    suspicious_length=suspicious_length,
                    source_offset=source_offset,
                    source_length=source_length,
                    candidate_text=_slice(
                        suspicious_text,
                        suspicious_offset,
                        suspicious_length,
                        suspicious_reference,
                    ),
                    source_text=_slice(
                        source_text,
                        source_offset,
                        source_length,
                        source_reference,
                    ),
                    category=_category(feature),
                )
            )
    return cases


def assign_source_group_splits(
    cases: list[PanCase],
    *,
    seed: int = 20260920,
    train_percent: int = 60,
    validation_percent: int = 20,
) -> None:
    """Assign deterministic splits while keeping each source document in one split."""

    if train_percent < 1 or validation_percent < 1 or train_percent + validation_percent >= 100:
        raise ValueError("Split percentages must leave non-zero train, validation, and test sets.")
    source_references = sorted(
        {case.source_reference for case in cases},
        key=lambda value: hashlib.sha256(f"{seed}:{value}".encode()).hexdigest(),
    )
    source_count = len(source_references)
    train_end = round(source_count * train_percent / 100)
    validation_end = train_end + round(source_count * validation_percent / 100)
    split_by_source = {
        source: (
            "train"
            if index < train_end
            else "validation"
            if index < validation_end
            else "test"
        )
        for index, source in enumerate(source_references)
    }
    for case in cases:
        case.split = split_by_source[case.source_reference]


def select_stratified_cases(
    cases: list[PanCase], limit: int, *, seed: int = 20260920
) -> list[PanCase]:
    """Select a deterministic near-balanced number of cases from each category."""

    if limit < 1:
        raise ValueError("The case limit must be a positive integer.")
    categories = sorted({case.category for case in cases})
    queues = {
        category: sorted(
            (case for case in cases if case.category == category),
            key=lambda case: hashlib.sha256(f"{seed}:{case.case_id}".encode()).hexdigest(),
        )
        for category in categories
    }
    selected: list[PanCase] = []
    while len(selected) < limit and any(queues.values()):
        for category in categories:
            if queues[category] and len(selected) < limit:
                selected.append(queues[category].pop(0))
    return selected


def export_manifest(cases: list[PanCase], output_path: Path, corpus_root: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dataset": "PAN-PC-11",
        "corpus_root": str(corpus_root.resolve()),
        "cases": len(cases),
        "source_groups": len({case.source_reference for case in cases}),
        "split_counts": dict(Counter(case.split for case in cases)),
        "category_counts": dict(Counter(case.category for case in cases)),
        "records": [asdict(case) for case in cases],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import PAN-PC-11 external plagiarism cases.")
    parser.add_argument("corpus_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--include-unknown-language", action="store_true")
    args = parser.parse_args()

    cases = load_pan_cases(
        args.corpus_root,
        include_unknown_language=args.include_unknown_language,
    )
    if args.limit is not None:
        cases = select_stratified_cases(cases, args.limit, seed=args.seed)
    assign_source_group_splits(cases, seed=args.seed)
    export_manifest(cases, args.output, args.corpus_root)
    print(f"Imported {len(cases)} PAN cases to {args.output}")


if __name__ == "__main__":
    main()
