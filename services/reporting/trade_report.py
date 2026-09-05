from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from services.local_paper.broker import _connect, get_account, positions

DUBAI = ZoneInfo("Asia/Dubai")
ASSET_CLASSES = ("Forex", "Commodities", "Indices", "Stocks", "Crypto", "ETFs", "Futures")


def trade_rows(*, asset_class: str | None = None, bot_id: str | None = None,
               campaign_id: str | None = None, limit: int = 1000) -> list[dict]:
    clauses, params = [], []
    for column, value in (("asset_class", asset_class), ("bot_id", bot_id), ("campaign_id", campaign_id)):
        if value:
            clauses.append(f"LOWER({column})=LOWER(?)" if column == "asset_class" else f"{column}=?")
            params.append(value)
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    with _connect() as conn:
        rows = conn.execute(
            f"SELECT * FROM trades{where} ORDER BY opened_at DESC LIMIT ?",
            (*params, min(max(limit, 1), 5000)),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["opened_at_display"] = datetime.fromtimestamp(item["opened_at"], DUBAI).isoformat()
        item["closed_at_display"] = (
            datetime.fromtimestamp(item["closed_at"], DUBAI).isoformat() if item["closed_at"] else None
        )
        result.append(item)
    return result


def _metrics(rows: list[dict]) -> dict:
    closed = [row for row in rows if row["status"] == "CLOSED" and row["net_pnl"] is not None]
    wins = [row for row in closed if float(row["net_pnl"]) > 0]
    losses = [row for row in closed if float(row["net_pnl"]) < 0]
    gross_profit = sum(float(row["net_pnl"]) for row in wins)
    gross_loss = abs(sum(float(row["net_pnl"]) for row in losses))
    return {
        "closed_trades": len(closed), "open_trades": sum(row["status"] == "OPEN" for row in rows),
        "wins": len(wins), "losses": len(losses), "breakeven": len(closed) - len(wins) - len(losses),
        "net_pnl": sum(float(row["net_pnl"]) for row in closed),
        "win_rate": len(wins) / len(closed) if closed else None,
        "gross_profit": gross_profit, "gross_loss": gross_loss,
        "profit_factor": gross_profit / gross_loss if gross_loss else None,
    }


def dashboard() -> dict:
    rows = trade_rows(limit=5000)
    by_asset, by_bot = defaultdict(list), defaultdict(list)
    for row in rows:
        by_asset[row["asset_class"]].append(row)
        by_bot[row["bot_id"]].append(row)
    return {
        "account": get_account(), "metrics": _metrics(rows),
        "by_asset": {key: _metrics(value) for key, value in sorted(by_asset.items())},
        "by_bot": {key: _metrics(value) for key, value in sorted(by_bot.items())},
        "open_positions": positions(), "reporting_currency": "USD",
        "display_timezone": "Asia/Dubai",
        "legacy_warning": "Legacy unprotected records are excluded from the canonical trade table.",
    }
