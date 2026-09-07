from __future__ import annotations

from datetime import datetime, timezone

from backend.app.services.market_data.lse_global import LSEGlobalMarketData
from services.local_paper.broker import apply_protection_bar, mark_price, positions


TIMEFRAMES = {
    "Stocks": "1d", "ETFs": "1d", "Indices": "1d", "Futures": "1d",
    "Forex": "1h", "Crypto": "1h", "Commodities": "4h",
}


def refresh_open_position_marks() -> dict:
    open_positions = positions()
    instruments = {
        row["instrument"]: TIMEFRAMES.get(row.get("asset_class"), "1d")
        for row in open_positions
    }
    updated, failures, auto_exits = [], [], []
    if not instruments:
        return {
            "ok": True, "source": "London Strategic Edge", "updated": [],
            "failed": [], "auto_exits": [],
            "marked_at": datetime.now(timezone.utc).isoformat(),
        }
    provider = LSEGlobalMarketData()
    for instrument, timeframe in instruments.items():
        try:
            rows = provider.candles(instrument, timeframe, 2)
            bar = rows[-1]
            price = float(bar["close"])
            mark_price(instrument, price)
            auto_exits.extend(apply_protection_bar(instrument, bar))
            updated.append({"instrument": instrument, "price": price, "timeframe": timeframe})
        except Exception:
            failures.append(instrument)
    return {
        "ok": bool(updated) or not instruments,
        "source": "London Strategic Edge",
        "marked_at": datetime.now(timezone.utc).isoformat(),
        "updated": updated, "failed": failures, "auto_exits": auto_exits,
    }
