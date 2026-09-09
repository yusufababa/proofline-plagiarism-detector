from __future__ import annotations

import hashlib
import re
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.domain import ReferenceDocument


UUID_PREFIX = re.compile(r"^[0-9a-f]{32}_", re.IGNORECASE)


class CorpusRepository:
    """SQLite metadata catalogue backed by document files on disk."""

    def __init__(self, database_path: Path, reference_dir: Path) -> None:
        self.database_path = database_path
        self.reference_dir = reference_dir

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _session(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._session() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reference_documents (
                    id TEXT PRIMARY KEY,
                    original_name TEXT NOT NULL,
                    stored_name TEXT NOT NULL UNIQUE,
                    extension TEXT NOT NULL,
                    sha256 TEXT NOT NULL UNIQUE,
                    size_bytes INTEGER NOT NULL,
                    added_at TEXT NOT NULL
                )
                """
            )

    def list_all(self) -> list[ReferenceDocument]:
        with self._session() as connection:
            rows = connection.execute(
                "SELECT * FROM reference_documents ORDER BY added_at DESC, original_name"
            ).fetchall()
        return [ReferenceDocument(**dict(row)) for row in rows]

    def find_by_hash(self, sha256: str) -> ReferenceDocument | None:
        with self._session() as connection:
            row = connection.execute(
                "SELECT * FROM reference_documents WHERE sha256 = ?",
                (sha256,),
            ).fetchone()
        return ReferenceDocument(**dict(row)) if row else None

    def add(self, original_name: str, stored_name: str, content: bytes) -> ReferenceDocument:
        document = ReferenceDocument(
            id=uuid4().hex,
            original_name=original_name,
            stored_name=stored_name,
            extension=Path(original_name).suffix.lower(),
            sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
            added_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        with self._session() as connection:
            connection.execute(
                """
                INSERT INTO reference_documents
                (id, original_name, stored_name, extension, sha256, size_bytes, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.original_name,
                    document.stored_name,
                    document.extension,
                    document.sha256,
                    document.size_bytes,
                    document.added_at,
                ),
            )
        return document

    def sync_existing_files(self, allowed_extensions: frozenset[str]) -> int:
        """Catalogue reference files created by an earlier app version."""

        known = {document.stored_name for document in self.list_all()}
        imported = 0
        for path in self.reference_dir.iterdir():
            if not path.is_file() or path.suffix.lower() not in allowed_extensions or path.name in known:
                continue
            content = path.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            if self.find_by_hash(digest):
                continue
            original_name = UUID_PREFIX.sub("", path.name)
            self.add(original_name, path.name, content)
            imported += 1
        return imported

    def path_for(self, document: ReferenceDocument) -> Path:
        return self.reference_dir / document.stored_name
