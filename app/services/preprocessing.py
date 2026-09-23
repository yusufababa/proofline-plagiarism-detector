import re
import unicodedata

from app.domain import Passage


WORD_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")
BIBLIOGRAPHY_HEADINGS = frozenset({
    "bibliography",
    "references",
    "reference list",
    "works cited",
    "literature cited",
})
BOILERPLATE_LINE_PATTERNS = (
    re.compile(r"^page\s+\d+(?:\s+of\s+\d+)?$", re.IGNORECASE),
    re.compile(r"^(?:student name|matric(?:ulation)? number|course code|department)\s*:.*$", re.IGNORECASE),
    re.compile(r"^(?:table of contents|copyright notice|all rights reserved)$", re.IGNORECASE),
)
CITATION_PATTERNS = (
    re.compile(r"\([^)]*\b(?:19|20)\d{2}[a-z]?[^)]*\)"),
    re.compile(r"\[(?:\d+)(?:\s*[,;-]\s*\d+)*\]"),
    re.compile(r"\b[A-Z][A-Za-z'-]+(?:\s+et al\.)?\s+\((?:19|20)\d{2}[a-z]?\)"),
)
QUOTED_TEXT_PATTERN = re.compile(r'"([^"\n]{20,})"')


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\u2018", "'").replace("\u2019", "'")
    normalized = normalized.replace("\u201c", '"').replace("\u201d", '"')
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def tokenize(text: str) -> list[str]:
    return WORD_PATTERN.findall(normalize_text(text).lower())


def contains_citation(text: str) -> bool:
    """Identify common author-year and numeric academic citation forms."""
    normalized = normalize_text(text)
    return any(pattern.search(normalized) for pattern in CITATION_PATTERNS)


def is_quotation(text: str) -> bool:
    """Return true when quoted wording forms at least half of a passage."""
    normalized = normalize_text(text)
    total_words = len(tokenize(normalized))
    if total_words == 0:
        return False
    quoted_words = sum(len(tokenize(match.group(1))) for match in QUOTED_TEXT_PATTERN.finditer(normalized))
    return quoted_words / total_words >= 0.5


def prepare_academic_text(text: str) -> str:
    """Remove bibliography content and simple document boilerplate before segmentation."""
    content_lines: list[str] = []
    for raw_line in text.splitlines():
        cleaned = normalize_text(raw_line)
        heading = re.sub(r"[^a-z ]", "", cleaned.lower()).strip()
        if heading in BIBLIOGRAPHY_HEADINGS:
            break
        if cleaned and any(pattern.fullmatch(cleaned) for pattern in BOILERPLATE_LINE_PATTERNS):
            continue
        content_lines.append(raw_line)
    return "\n".join(content_lines)


def split_passages(text: str, minimum_words: int = 5) -> list[Passage]:
    passages: list[Passage] = []
    prepared = prepare_academic_text(text)
    for raw in SENTENCE_BOUNDARY.split(prepared):
        cleaned = normalize_text(raw)
        if len(tokenize(cleaned)) >= minimum_words:
            passages.append(
                Passage(
                    text=cleaned,
                    index=len(passages),
                    is_quotation=is_quotation(cleaned),
                    has_citation=contains_citation(cleaned),
                )
            )
    return passages
