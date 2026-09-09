import re
import unicodedata

from app.domain import Passage


WORD_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\u2018", "'").replace("\u2019", "'")
    normalized = normalized.replace("\u201c", '"').replace("\u201d", '"')
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def tokenize(text: str) -> list[str]:
    return WORD_PATTERN.findall(normalize_text(text).lower())


def split_passages(text: str, minimum_words: int = 5) -> list[Passage]:
    passages: list[Passage] = []
    for raw in SENTENCE_BOUNDARY.split(text):
        cleaned = normalize_text(raw)
        if len(tokenize(cleaned)) >= minimum_words:
            passages.append(Passage(text=cleaned, index=len(passages)))
    return passages
