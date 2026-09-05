from __future__ import annotations

import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path("/Users/macmac/Documents/Codex/FX")
DB_PATH = ROOT / "data" / "campaigns" / "campaigns.sqlite3"
TARGET_TYPES = {"PROFIT_DOLLARS", "PROFIT_PERCENT", "ENDING_BALANCE"}


class CampaignStore:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS campaigns(
                    campaign_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
                    account_id TEXT NOT NULL, bot_id TEXT NOT NULL,
                    strategy_id TEXT NOT NULL, strategy_version TEXT NOT NULL,
                    instrument TEXT NOT NULL, asset_class TEXT NOT NULL,
                    capital REAL NOT NULL, target_type TEXT NOT NULL,
                    target_value REAL NOT NULL, maximum_loss REAL NOT NULL,
                    deadline REAL NOT NULL, realized_pnl REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL, readiness_reason TEXT NOT NULL,
                    created_at REAL NOT NULL, updated_at REAL NOT NULL,
                    approved_at REAL, stopped_at REAL
                );
                CREATE INDEX IF NOT EXISTS idx_campaign_status ON campaigns(status);
                """
            )

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def create(self, *, bot_id: str, strategy_id: str, strategy_version: str,
               instrument: str, asset_class: str, capital: float,
               target_type: str, target_value: float, maximum_loss: float,
               deadline: float, owner_id: str = "local-owner",
               account_id: str = "local-paper") -> dict[str, Any]:
        target_type = target_type.upper()
        if target_type not in TARGET_TYPES:
            raise ValueError("Target type must be profit dollars, profit percent, or ending balance.")
        if min(capital, target_value, maximum_loss) <= 0:
            raise ValueError("Capital, target, and maximum loss must be positive.")
        if maximum_loss > capital:
            raise ValueError("Maximum campaign loss cannot exceed allocated capital.")
        if deadline <= time.time():
            raise ValueError("Campaign deadline must be in the future.")
        if target_type == "ENDING_BALANCE" and target_value <= capital:
            raise ValueError("Ending-balance target must be greater than starting capital.")
        now = time.time()
        campaign_id = str(uuid.uuid4())
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO campaigns(
                    campaign_id,owner_id,account_id,bot_id,strategy_id,strategy_version,
                    instrument,asset_class,capital,target_type,target_value,maximum_loss,
                    deadline,realized_pnl,status,readiness_reason,created_at,updated_at,
                    approved_at,stopped_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (campaign_id, owner_id, account_id, bot_id, strategy_id, strategy_version,
                 instrument, asset_class, capital, target_type, target_value, maximum_loss,
                 deadline, 0.0, "DRAFT", "Readiness must be checked before activation.",
                 now, now, None, None),
            )
        return self.get(campaign_id)

    def get(self, campaign_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
        if not row:
            raise ValueError("Campaign not found.")
        return dict(row)

    def list(self, limit: int = 200) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM campaigns ORDER BY created_at DESC LIMIT ?",
                                (min(max(limit, 1), 1000),)).fetchall()
        return [dict(row) for row in rows]

    def set_status(self, campaign_id: str, status: str, reason: str) -> dict[str, Any]:
        allowed = {"DRAFT", "WAITING_FOR_READINESS", "ACTIVE", "PAUSED", "COMPLETED", "EXPIRED", "STOPPED"}
        status = status.upper()
        if status not in allowed:
            raise ValueError("Invalid campaign state.")
        now = time.time()
        approved_at = now if status == "ACTIVE" else None
        stopped_at = now if status in {"COMPLETED", "EXPIRED", "STOPPED"} else None
        with self._connect() as conn:
            found = conn.execute("SELECT 1 FROM campaigns WHERE campaign_id=?", (campaign_id,)).fetchone()
            if not found:
                raise ValueError("Campaign not found.")
            conn.execute(
                """UPDATE campaigns SET status=?,readiness_reason=?,updated_at=?,
                   approved_at=COALESCE(?,approved_at),stopped_at=COALESCE(?,stopped_at)
                   WHERE campaign_id=?""",
                (status, reason, now, approved_at, stopped_at, campaign_id),
            )
        return self.get(campaign_id)


campaign_store = CampaignStore()
