from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class StoredUpload:
    original_name: str
    stored_name: str
    path: Path
    content: bytes
    sha256: str


def validate_filename(filename: str | None, allowed_extensions: frozenset[str]) -> str:
    name = Path(filename or "document.txt").name
    if Path(name).suffix.lower() not in allowed_extensions:
        supported = ", ".join(sorted(allowed_extensions))
        raise ValueError(f"Unsupported file type. Use one of: {supported}.")
    return name


def store_upload(
    filename: str | None,
    content: bytes,
    destination_dir: Path,
    allowed_extensions: frozenset[str],
) -> StoredUpload:
    safe_name = validate_filename(filename, allowed_extensions)
    stored_name = f"{uuid4().hex}_{safe_name}"
    path = destination_dir / stored_name
    path.write_bytes(content)
    return StoredUpload(
        original_name=safe_name,
        stored_name=stored_name,
        path=path,
        content=content,
        sha256=sha256(content).hexdigest(),
    )

