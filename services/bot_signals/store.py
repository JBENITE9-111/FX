from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager

from dataclasses import (
    asdict,
    dataclass,
)
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

DB_PATH = (
    ROOT
    / "data"
    / "bot_signals"
    / "signals.sqlite3"
)


@dataclass
class BotSignal:
    signal_id: str

    bot_id: str
    bot_name: str

    instrument: str
    asset_class: str

    strategy_id: str

    direction: str

    score: float

    entry: float | None

    stop: float | None

    target_1: float | None

    target_2: float | None

    expected_r: float | None

    confidence: float | None

    risk_status: str

    eligibility: str

    reason: str

    data_source: str

    timeframe: str

    created_at: float

    expires_at: float | None = None

    structural_invalidation: float | str | None = None
    profit_plan: str | None = None
    strategy_version: str = "1"
    market_data_asof: float | None = None
    confidence_label: str = "UNVERIFIED_SCORE"

    metadata: dict[str, Any] | None = None


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.row_factory = (
        sqlite3.Row
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_signals (
            signal_id TEXT PRIMARY KEY,

            bot_id TEXT NOT NULL,
            bot_name TEXT NOT NULL,

            instrument TEXT NOT NULL,
            asset_class TEXT NOT NULL,

            strategy_id TEXT NOT NULL,

            direction TEXT NOT NULL,

            score REAL NOT NULL,

            entry REAL,
            stop REAL,
            target_1 REAL,
            target_2 REAL,

            expected_r REAL,
            confidence REAL,

            risk_status TEXT NOT NULL,
            eligibility TEXT NOT NULL,

            reason TEXT NOT NULL,

            data_source TEXT NOT NULL,
            timeframe TEXT NOT NULL,

            created_at REAL NOT NULL,
            expires_at REAL,

            structural_invalidation TEXT,
            profit_plan TEXT,
            strategy_version TEXT NOT NULL DEFAULT '1',
            market_data_asof REAL,
            confidence_label TEXT NOT NULL DEFAULT 'UNVERIFIED_SCORE',

            metadata_json TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_bot_signals_created
        ON bot_signals(created_at DESC)
        """
    )

    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_bot_signals_bot
        ON bot_signals(bot_id)
        """
    )

    existing = {row[1] for row in conn.execute("PRAGMA table_info(bot_signals)")}
    for name, definition in {
        "structural_invalidation": "TEXT", "profit_plan": "TEXT",
        "strategy_version": "TEXT NOT NULL DEFAULT '1'", "market_data_asof": "REAL",
        "confidence_label": "TEXT NOT NULL DEFAULT 'UNVERIFIED_SCORE'",
    }.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE bot_signals ADD COLUMN {name} {definition}")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def save_signal(
    signal: BotSignal,
) -> BotSignal:

    with _connect() as conn:

        conn.execute(
            """
            INSERT OR REPLACE
            INTO bot_signals(
                signal_id,
                bot_id,
                bot_name,
                instrument,
                asset_class,
                strategy_id,
                direction,
                score,
                entry,
                stop,
                target_1,
                target_2,
                expected_r,
                confidence,
                risk_status,
                eligibility,
                reason,
                data_source,
                timeframe,
                created_at,
                expires_at,
                structural_invalidation,
                profit_plan,
                strategy_version,
                market_data_asof,
                confidence_label,
                metadata_json
            )
            VALUES(
                ?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?,?,?,?,
                ?,?,?,?,?,?,?
            )
            """,
            (
                signal.signal_id,

                signal.bot_id,
                signal.bot_name,

                signal.instrument,
                signal.asset_class,

                signal.strategy_id,

                signal.direction,

                signal.score,

                signal.entry,
                signal.stop,
                signal.target_1,
                signal.target_2,

                signal.expected_r,
                signal.confidence,

                signal.risk_status,
                signal.eligibility,

                signal.reason,

                signal.data_source,
                signal.timeframe,

                signal.created_at,
                signal.expires_at,

                signal.structural_invalidation,
                signal.profit_plan,
                signal.strategy_version,
                signal.market_data_asof,
                signal.confidence_label,

                json.dumps(
                    signal.metadata
                    or {}
                ),
            ),
        )

    return signal


def create_signal(
    *,
    bot_id: str,
    bot_name: str,

    instrument: str,
    asset_class: str,

    strategy_id: str,

    direction: str,

    score: float,

    entry: float | None = None,

    stop: float | None = None,

    target_1: float | None = None,

    target_2: float | None = None,

    expected_r: float | None = None,

    confidence: float | None = None,

    risk_status: str = "PENDING",

    eligibility: str = "RESEARCH_ONLY",

    reason: str = "",

    data_source: str = (
        "London Strategic Edge"
    ),

    timeframe: str = "1h",

    ttl_seconds: int = 3600,

    structural_invalidation: float | str | None = None,

    profit_plan: str | None = None,

    strategy_version: str = "1",

    market_data_asof: float | None = None,

    metadata: dict | None = None,
) -> BotSignal:

    now = time.time()

    signal = BotSignal(
        signal_id=str(
            uuid.uuid4()
        ),

        bot_id=bot_id,
        bot_name=bot_name,

        instrument=instrument,
        asset_class=asset_class,

        strategy_id=strategy_id,

        direction=(
            direction
            .strip()
            .upper()
        ),

        score=float(
            score
        ),

        entry=entry,

        stop=stop,

        target_1=target_1,

        target_2=target_2,

        expected_r=expected_r,

        confidence=confidence,

        risk_status=risk_status,

        eligibility=eligibility,

        reason=reason,

        data_source=data_source,

        timeframe=timeframe,

        created_at=now,

        expires_at=(
            now
            + ttl_seconds
        ),

        structural_invalidation=structural_invalidation,
        profit_plan=profit_plan,
        strategy_version=strategy_version,
        market_data_asof=market_data_asof,
        confidence_label="CALIBRATED_PROBABILITY" if confidence is not None else "UNVERIFIED_SCORE",

        metadata=metadata or {},
    )

    return save_signal(
        signal
    )


def list_signals(
    *,
    limit: int = 200,
) -> list[dict]:

    now = time.time()

    with _connect() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM bot_signals

            WHERE
                expires_at IS NULL
                OR expires_at > ?

            ORDER BY
                created_at DESC

            LIMIT ?
            """,
            (
                now,
                limit,
            ),
        ).fetchall()

    results = []

    for row in rows:

        item = dict(
            row
        )

        item["metadata"] = (
            json.loads(
                item.pop(
                    "metadata_json"
                )
                or "{}"
            )
        )

        results.append(
            item
        )

    return results


def get_signal(
    signal_id: str,
) -> dict | None:

    with _connect() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM bot_signals
            WHERE signal_id=?
            """,
            (
                signal_id,
            ),
        ).fetchone()

    if not row:
        return None

    item = dict(row)

    item["metadata"] = json.loads(
        item.pop(
            "metadata_json"
        )
        or "{}"
    )

    return item
