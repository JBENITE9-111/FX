from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

ROOT = Path("/Users/macmac/Documents/Codex/FX")
DB_PATH = ROOT / "data" / "operations" / "operations.sqlite3"


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize() -> None:
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS favorites(
                favorite_id TEXT PRIMARY KEY, instrument_id TEXT NOT NULL,
                symbol TEXT NOT NULL, name TEXT NOT NULL, asset_class TEXT NOT NULL,
                provider TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
                state TEXT NOT NULL DEFAULT 'WATCHING', risk_state TEXT NOT NULL DEFAULT 'UNKNOWN',
                execution_timeframe TEXT NOT NULL, context_timeframes_json TEXT NOT NULL,
                strategy_id TEXT NOT NULL, bot_id TEXT NOT NULL,
                min_evidence REAL, min_rr REAL NOT NULL DEFAULT 1.5,
                channels_json TEXT NOT NULL, event_types_json TEXT NOT NULL,
                last_analysis_at REAL, created_at REAL NOT NULL, updated_at REAL NOT NULL,
                UNIQUE(instrument_id)
            );
            CREATE TABLE IF NOT EXISTS events(
                event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, source TEXT NOT NULL,
                subject_type TEXT NOT NULL, subject_id TEXT NOT NULL, state TEXT,
                occurred_at REAL NOT NULL, market_data_asof REAL, provider TEXT,
                payload_json TEXT NOT NULL, evidence_ids_json TEXT NOT NULL,
                versions_json TEXT NOT NULL, input_hash TEXT, output_hash TEXT,
                dedup_key TEXT, UNIQUE(dedup_key)
            );
            CREATE TABLE IF NOT EXISTS reports(
                report_id TEXT PRIMARY KEY, report_type TEXT NOT NULL,
                subject_id TEXT NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL,
                generated_at REAL NOT NULL, body_json TEXT NOT NULL,
                evidence_ids_json TEXT NOT NULL, provenance_json TEXT NOT NULL,
                report_version TEXT NOT NULL, input_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS schedules(
                schedule_id TEXT PRIMARY KEY, favorite_id TEXT,
                action TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
                interval_minutes INTEGER NOT NULL, timezone TEXT NOT NULL,
                execution_timeframe TEXT NOT NULL, context_timeframes_json TEXT NOT NULL,
                strategy_id TEXT NOT NULL, bot_id TEXT NOT NULL,
                channels_json TEXT NOT NULL, event_types_json TEXT NOT NULL,
                last_run_at REAL, next_run_at REAL NOT NULL, lease_until REAL,
                created_at REAL NOT NULL, updated_at REAL NOT NULL,
                FOREIGN KEY(favorite_id) REFERENCES favorites(favorite_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS schedule_runs(
                run_id TEXT PRIMARY KEY, schedule_id TEXT NOT NULL,
                started_at REAL NOT NULL, completed_at REAL, status TEXT NOT NULL,
                summary TEXT NOT NULL, event_id TEXT, report_id TEXT,
                FOREIGN KEY(schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS notification_deliveries(
                delivery_id TEXT PRIMARY KEY, event_id TEXT NOT NULL, channel TEXT NOT NULL,
                status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
                dedup_key TEXT NOT NULL, requested_at REAL NOT NULL,
                delivered_at REAL, next_attempt_at REAL, last_error TEXT,
                rendered_message TEXT NOT NULL, UNIQUE(dedup_key, channel)
            );
            CREATE TABLE IF NOT EXISTS goal_plans(
                goal_id TEXT PRIMARY KEY, name TEXT NOT NULL, success_metrics_json TEXT NOT NULL,
                baseline TEXT NOT NULL, hypothesis TEXT NOT NULL, experiment_plan TEXT NOT NULL,
                data_needed_json TEXT NOT NULL, participants_json TEXT NOT NULL,
                risk_constraints_json TEXT NOT NULL, validation_method TEXT NOT NULL,
                pass_threshold TEXT NOT NULL, progress TEXT NOT NULL,
                next_action TEXT NOT NULL, stop_conditions_json TEXT NOT NULL,
                created_at REAL NOT NULL, updated_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_events_time ON events(occurred_at DESC);
            CREATE INDEX IF NOT EXISTS idx_schedules_due ON schedules(enabled,next_run_at);
            CREATE INDEX IF NOT EXISTS idx_deliveries_status ON notification_deliveries(status,next_attempt_at);
            """
        )
        # Discord is the sole external delivery channel. Keep the local inbox for
        # auditability and migrate existing favorites/schedules to the same policy.
        channels = json.dumps(["app", "discord"])
        conn.execute("UPDATE favorites SET channels_json=?", (channels,))
        conn.execute("UPDATE schedules SET channels_json=?", (channels,))


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _decoded(row: sqlite3.Row | None, fields: tuple[str, ...]) -> dict | None:
    if row is None:
        return None
    item = dict(row)
    for field in fields:
        if field in item:
            item[field.removesuffix("_json")] = json.loads(item.pop(field) or "null")
    for key in ("enabled",):
        if key in item:
            item[key] = bool(item[key])
    return item


def save_favorite(data: dict[str, Any]) -> dict:
    initialize()
    now = time.time()
    instrument_id = str(data["instrument_id"]).strip()
    favorite_id = str(data.get("favorite_id") or uuid.uuid4())
    with connection() as conn:
        existing = conn.execute("SELECT favorite_id,created_at FROM favorites WHERE instrument_id=?", (instrument_id,)).fetchone()
        if existing:
            favorite_id, created_at = existing["favorite_id"], existing["created_at"]
        else:
            created_at = now
        conn.execute(
            """INSERT INTO favorites VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(instrument_id) DO UPDATE SET
              symbol=excluded.symbol,name=excluded.name,asset_class=excluded.asset_class,
              provider=excluded.provider,enabled=excluded.enabled,state=excluded.state,
              risk_state=excluded.risk_state,execution_timeframe=excluded.execution_timeframe,
              context_timeframes_json=excluded.context_timeframes_json,
              strategy_id=excluded.strategy_id,bot_id=excluded.bot_id,
              min_evidence=excluded.min_evidence,min_rr=excluded.min_rr,
              channels_json=excluded.channels_json,event_types_json=excluded.event_types_json,
              last_analysis_at=COALESCE(excluded.last_analysis_at,favorites.last_analysis_at),
              updated_at=excluded.updated_at""",
            (favorite_id, instrument_id, str(data["symbol"]).strip(), str(data.get("name") or data["symbol"]).strip(),
             str(data["asset_class"]), str(data.get("provider") or "London Strategic Edge"), int(bool(data.get("enabled", True))),
             str(data.get("state") or "WATCHING"), str(data.get("risk_state") or "UNKNOWN"),
             str(data.get("execution_timeframe") or "1h"), _json(data.get("context_timeframes") or ["4h"]),
             str(data.get("strategy_id") or "model_council"), str(data.get("bot_id") or "trading_team"),
             data.get("min_evidence"), float(data.get("min_rr") or 1.5), _json(data.get("channels") or ["app"]),
             _json(data.get("event_types") or ["signal.state_changed", "risk.vetoed", "system.health_changed"]),
             data.get("last_analysis_at"), created_at, now),
        )
    return get_favorite(favorite_id) or {}


def get_favorite(favorite_id: str) -> dict | None:
    initialize()
    with connection() as conn:
        row = conn.execute("SELECT * FROM favorites WHERE favorite_id=?", (favorite_id,)).fetchone()
    return _decoded(row, ("context_timeframes_json", "channels_json", "event_types_json"))


def list_favorites() -> list[dict]:
    initialize()
    with connection() as conn:
        rows = conn.execute("SELECT * FROM favorites ORDER BY asset_class,symbol").fetchall()
    return [_decoded(row, ("context_timeframes_json", "channels_json", "event_types_json")) or {} for row in rows]


def delete_favorite(favorite_id: str) -> bool:
    initialize()
    with connection() as conn:
        changed = conn.execute("DELETE FROM favorites WHERE favorite_id=?", (favorite_id,)).rowcount
    return bool(changed)


def record_event(*, event_type: str, source: str, subject_type: str, subject_id: str,
                 payload: dict[str, Any], state: str | None = None, provider: str | None = None,
                 market_data_asof: float | None = None, evidence_ids: list[str] | None = None,
                 versions: dict[str, str] | None = None, input_hash: str | None = None,
                 dedup_key: str | None = None) -> dict:
    initialize()
    occurred_at = time.time()
    body = _json(payload)
    event_id = str(uuid.uuid4())
    output_hash = hashlib.sha256(body.encode()).hexdigest()
    with connection() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (event_id, event_type, source, subject_type, subject_id, state, occurred_at,
             market_data_asof, provider, body, _json(evidence_ids or []), _json(versions or {}),
             input_hash, output_hash, dedup_key),
        )
        if not conn.execute("SELECT 1 FROM events WHERE event_id=?", (event_id,)).fetchone() and dedup_key:
            row = conn.execute("SELECT * FROM events WHERE dedup_key=?", (dedup_key,)).fetchone()
        else:
            row = conn.execute("SELECT * FROM events WHERE event_id=?", (event_id,)).fetchone()
    return _decoded(row, ("payload_json", "evidence_ids_json", "versions_json")) or {}


def list_events(limit: int = 100) -> list[dict]:
    initialize()
    with connection() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY occurred_at DESC LIMIT ?", (min(max(limit, 1), 500),)).fetchall()
    return [_decoded(row, ("payload_json", "evidence_ids_json", "versions_json")) or {} for row in rows]


def save_report(*, report_type: str, subject_id: str, title: str, status: str,
                body: dict[str, Any], evidence_ids: list[str], provenance: dict[str, Any],
                input_hash: str, report_version: str = "1.0") -> dict:
    initialize()
    report_id = str(uuid.uuid4())
    with connection() as conn:
        conn.execute("INSERT INTO reports VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                     (report_id, report_type, subject_id, title, status, time.time(), _json(body),
                      _json(evidence_ids), _json(provenance), report_version, input_hash))
        row = conn.execute("SELECT * FROM reports WHERE report_id=?", (report_id,)).fetchone()
    return _decoded(row, ("body_json", "evidence_ids_json", "provenance_json")) or {}


def get_report(report_id: str) -> dict | None:
    initialize()
    with connection() as conn:
        row = conn.execute("SELECT * FROM reports WHERE report_id=?", (report_id,)).fetchone()
    return _decoded(row, ("body_json", "evidence_ids_json", "provenance_json"))


def list_reports(limit: int = 100) -> list[dict]:
    initialize()
    with connection() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY generated_at DESC LIMIT ?", (min(max(limit, 1), 500),)).fetchall()
    return [_decoded(row, ("body_json", "evidence_ids_json", "provenance_json")) or {} for row in rows]


def save_schedule(data: dict[str, Any]) -> dict:
    initialize()
    now = time.time()
    interval = min(max(int(data.get("interval_minutes") or 60), 5), 10080)
    schedule_id = str(data.get("schedule_id") or "")
    if not schedule_id and data.get("favorite_id"):
        with connection() as conn:
            existing = conn.execute("SELECT schedule_id FROM schedules WHERE favorite_id=? AND action=? LIMIT 1",
                                    (data["favorite_id"], str(data.get("action") or "generate_report"))).fetchone()
        schedule_id = existing["schedule_id"] if existing else ""
    schedule_id = schedule_id or str(uuid.uuid4())
    with connection() as conn:
        conn.execute("""INSERT INTO schedules VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
          ON CONFLICT(schedule_id) DO UPDATE SET enabled=excluded.enabled,interval_minutes=excluded.interval_minutes,
          timezone=excluded.timezone,execution_timeframe=excluded.execution_timeframe,
          context_timeframes_json=excluded.context_timeframes_json,strategy_id=excluded.strategy_id,
          bot_id=excluded.bot_id,channels_json=excluded.channels_json,event_types_json=excluded.event_types_json,
          next_run_at=excluded.next_run_at,updated_at=excluded.updated_at""",
          (schedule_id, data.get("favorite_id"), str(data.get("action") or "generate_report"), int(bool(data.get("enabled", True))),
           interval, str(data.get("timezone") or "Asia/Dubai"), str(data.get("execution_timeframe") or "1h"),
           _json(data.get("context_timeframes") or ["4h"]), str(data.get("strategy_id") or "model_council"),
           str(data.get("bot_id") or "trading_team"), _json(data.get("channels") or ["app"]),
           _json(data.get("event_types") or ["report.generated"]), data.get("last_run_at"),
           float(data.get("next_run_at") or now + interval * 60), None, now, now))
    return get_schedule(schedule_id) or {}


def get_schedule(schedule_id: str) -> dict | None:
    initialize()
    with connection() as conn:
        row = conn.execute("SELECT * FROM schedules WHERE schedule_id=?", (schedule_id,)).fetchone()
    return _decoded(row, ("context_timeframes_json", "channels_json", "event_types_json"))


def list_schedules() -> list[dict]:
    initialize()
    with connection() as conn:
        rows = conn.execute("SELECT * FROM schedules ORDER BY next_run_at").fetchall()
    return [_decoded(row, ("context_timeframes_json", "channels_json", "event_types_json")) or {} for row in rows]


def set_schedule_enabled(schedule_id: str, enabled: bool) -> dict | None:
    initialize()
    with connection() as conn:
        conn.execute("UPDATE schedules SET enabled=?,lease_until=NULL,updated_at=? WHERE schedule_id=?",
                     (int(enabled), time.time(), schedule_id))
    return get_schedule(schedule_id)


def make_schedule_due(schedule_id: str) -> dict | None:
    initialize()
    with connection() as conn:
        conn.execute("UPDATE schedules SET enabled=1,next_run_at=0,lease_until=NULL,updated_at=? WHERE schedule_id=?",
                     (time.time(), schedule_id))
    return get_schedule(schedule_id)


def delete_schedule(schedule_id: str) -> bool:
    initialize()
    with connection() as conn:
        changed = conn.execute("DELETE FROM schedules WHERE schedule_id=?", (schedule_id,)).rowcount
    return bool(changed)


def claim_due_schedules(limit: int = 10) -> list[dict]:
    initialize()
    now = time.time()
    claimed: list[dict] = []
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        rows = conn.execute("SELECT * FROM schedules WHERE enabled=1 AND next_run_at<=? AND (lease_until IS NULL OR lease_until<?) ORDER BY next_run_at LIMIT ?", (now, now, limit)).fetchall()
        for row in rows:
            conn.execute("UPDATE schedules SET lease_until=? WHERE schedule_id=?", (now + 120, row["schedule_id"]))
            claimed.append(_decoded(row, ("context_timeframes_json", "channels_json", "event_types_json")) or {})
    return claimed


def finish_schedule(schedule: dict, *, status: str, summary: str, event_id: str | None = None,
                    report_id: str | None = None) -> None:
    now = time.time()
    run_id = str(uuid.uuid4())
    with connection() as conn:
        conn.execute("INSERT INTO schedule_runs VALUES(?,?,?,?,?,?,?,?)",
                     (run_id, schedule["schedule_id"], now, now, status, summary, event_id, report_id))
        conn.execute("UPDATE schedules SET last_run_at=?,next_run_at=?,lease_until=NULL,updated_at=? WHERE schedule_id=?",
                     (now, now + int(schedule["interval_minutes"]) * 60, now, schedule["schedule_id"]))


def queue_delivery(*, event_id: str, channel: str, dedup_key: str, message: str) -> dict:
    initialize()
    delivery_id = str(uuid.uuid4())
    with connection() as conn:
        conn.execute("INSERT OR IGNORE INTO notification_deliveries VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                     (delivery_id, event_id, channel, "PENDING", 0, dedup_key, time.time(), None, time.time(), None, message))
        row = conn.execute("SELECT * FROM notification_deliveries WHERE dedup_key=? AND channel=?", (dedup_key, channel)).fetchone()
    return dict(row) if row else {}


def due_deliveries(limit: int = 20) -> list[dict]:
    initialize()
    with connection() as conn:
        rows = conn.execute("SELECT * FROM notification_deliveries WHERE status IN ('PENDING','RETRY') AND (next_attempt_at IS NULL OR next_attempt_at<=?) ORDER BY requested_at LIMIT ?", (time.time(), limit)).fetchall()
    return [dict(row) for row in rows]


def update_delivery(delivery_id: str, *, status: str, error: str | None = None) -> None:
    now = time.time()
    with connection() as conn:
        row = conn.execute("SELECT attempts FROM notification_deliveries WHERE delivery_id=?", (delivery_id,)).fetchone()
        attempts = int(row["attempts"] if row else 0) + 1
        retry = now + min(3600, 30 * 2 ** max(0, attempts - 1)) if status == "RETRY" else None
        conn.execute("UPDATE notification_deliveries SET status=?,attempts=?,delivered_at=?,next_attempt_at=?,last_error=? WHERE delivery_id=?",
                     (status, attempts, now if status == "SENT" else None, retry, (error or "")[:500] or None, delivery_id))


def list_deliveries(limit: int = 100) -> list[dict]:
    initialize()
    with connection() as conn:
        rows = conn.execute("SELECT * FROM notification_deliveries ORDER BY requested_at DESC LIMIT ?", (min(max(limit, 1), 500),)).fetchall()
    return [dict(row) for row in rows]


initialize()
