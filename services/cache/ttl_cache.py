from __future__ import annotations

import json
import sqlite3
import threading
import time

from pathlib import Path
from typing import Any


class SQLiteTTLCache:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cache_expires "
                "ON cache(expires_at)"
            )

    def _connect(self):
        return sqlite3.connect(self.path)

    def set(self, key: str, value: Any, ttl_seconds: float) -> None:
        now = time.time()
        expires_at = now + max(0.0, float(ttl_seconds))

        payload = json.dumps(
            value,
            default=str,
            separators=(",", ":"),
        )

        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cache(key, value, expires_at, updated_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at
                """,
                (key, payload, expires_at, now),
            )

    def get(self, key: str) -> Any | None:
        now = time.time()

        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key=?",
                (key,),
            ).fetchone()

            if not row:
                return None

            value, expires_at = row

            if float(expires_at) <= now:
                conn.execute(
                    "DELETE FROM cache WHERE key=?",
                    (key,),
                )
                return None

            return json.loads(value)

    def delete(self, key: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                "DELETE FROM cache WHERE key=?",
                (key,),
            )

    def purge_expired(self) -> int:
        now = time.time()

        with self._lock, self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at <= ?",
                (now,),
            )
            return int(cursor.rowcount or 0)
