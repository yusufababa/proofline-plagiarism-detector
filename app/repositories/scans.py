from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.domain import ScanRecord, ScanResult


class ScanRepository:
    """Stores scan summaries and their explainable result payloads in SQLite."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

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
                CREATE TABLE IF NOT EXISTS scan_records (
                    id TEXT PRIMARY KEY,
                    submitted_document TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    model_mode TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    total_passages INTEGER NOT NULL,
                    matched_passages INTEGER NOT NULL,
                    reviewable_passages INTEGER NOT NULL,
                    excluded_passages INTEGER NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )

    def save(self, result: ScanResult) -> ScanRecord:
        record = ScanRecord(
            id=uuid4().hex,
            submitted_document=result.submitted_document,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            model_mode=result.model_mode,
            overall_score=result.overall_score,
            total_passages=result.total_passages,
            matched_passages=result.matched_passages,
            reviewable_passages=result.reviewable_passages,
            excluded_passages=result.excluded_passages,
        )
        with self._session() as connection:
            connection.execute(
                """
                INSERT INTO scan_records (
                    id, submitted_document, created_at, model_mode, overall_score,
                    total_passages, matched_passages, reviewable_passages,
                    excluded_passages, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.submitted_document,
                    record.created_at,
                    record.model_mode,
                    record.overall_score,
                    record.total_passages,
                    record.matched_passages,
                    record.reviewable_passages,
                    record.excluded_passages,
                    json.dumps(result.to_dict(), ensure_ascii=False),
                ),
            )
        return record

    def list_recent(self, limit: int = 50) -> list[ScanRecord]:
        safe_limit = min(max(limit, 1), 100)
        with self._session() as connection:
            rows = connection.execute(
                """
                SELECT id, submitted_document, created_at, model_mode, overall_score,
                       total_passages, matched_passages, reviewable_passages,
                       excluded_passages
                FROM scan_records
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [ScanRecord(**dict(row)) for row in rows]

    def get_result(self, scan_id: str) -> dict | None:
        with self._session() as connection:
            row = connection.execute(
                "SELECT id, created_at, result_json FROM scan_records WHERE id = ?",
                (scan_id,),
            ).fetchone()
        if row is None:
            return None
        result = json.loads(row["result_json"])
        result.update(
            {
                "scan_id": row["id"],
                "created_at": row["created_at"],
                "report_url": f"/api/scans/{row['id']}/report",
            }
        )
        return result

    def delete(self, scan_id: str) -> bool:
        with self._session() as connection:
            cursor = connection.execute("DELETE FROM scan_records WHERE id = ?", (scan_id,))
        return cursor.rowcount > 0

    def clear(self) -> int:
        with self._session() as connection:
            cursor = connection.execute("DELETE FROM scan_records")
        return max(cursor.rowcount, 0)
