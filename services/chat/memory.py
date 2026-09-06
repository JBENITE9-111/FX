from __future__ import annotations

import sqlite3
import time
import re
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path("/Users/macmac/Documents/Codex/FX/data/chat/personal_memory.sqlite3")


@contextmanager
def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user','assistant')),
        content TEXT NOT NULL,
        symbol TEXT,
        created_at REAL NOT NULL
    )""")
    connection.commit()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def remember(conversation_id: str, role: str, content: str, symbol: str | None = None) -> None:
    with _connect() as connection:
        connection.execute("INSERT INTO messages(conversation_id,role,content,symbol,created_at) VALUES(?,?,?,?,?)", (conversation_id[:80], role, content, symbol, time.time()))


def recent(conversation_id: str = "personal", limit: int = 24) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute("SELECT role,content,symbol,created_at FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT ?", (conversation_id[:80], max(1, min(limit, 100)))).fetchall()
    return [dict(row) for row in reversed(rows)]


def recall(query: str, conversation_id: str = "personal", limit: int = 12) -> list[dict]:
    """Recall older personal messages by meaningful terms while keeping data local."""
    terms = []
    for term in re.findall(r"[a-zA-Z0-9./_-]{3,}", query.lower()):
        if term not in terms and term not in {"what", "when", "where", "which", "about", "from", "with", "this", "that"}:
            terms.append(term)
    if not terms:
        return []
    clauses = " OR ".join("lower(content) LIKE ?" for _ in terms[:8])
    values = [f"%{term}%" for term in terms[:8]]
    with _connect() as connection:
        rows = connection.execute(
            f"SELECT role,content,symbol,created_at FROM messages WHERE conversation_id=? AND ({clauses}) ORDER BY id DESC LIMIT ?",
            [conversation_id[:80], *values, max(1, min(limit, 30))],
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def status() -> dict:
    with _connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    return {"stored_messages": count, "storage": "local SQLite on this Mac", "path": str(DB_PATH), "cloud_sync": False}
