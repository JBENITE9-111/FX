from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path("/Users/macmac/Documents/Codex/FX")
CATALOG_PATH = ROOT / "data" / "catalog" / "lse_catalog.json"
SUPPORTED_ASSET_CLASSES = ("Stocks", "ETFs", "Indices", "Forex", "Commodities", "Crypto", "Futures")
DEFAULT_TIMEFRAMES = {
    "Stocks": "1d", "ETFs": "1d", "Indices": "1d", "Futures": "1d",
    "Forex": "1h", "Crypto": "1h", "Commodities": "4h",
}

APPROVED_TRAINING_UNIVERSE = (
    {"instrument_id": "US_AAPL", "symbol": "AAPL", "name": "Apple", "asset_class": "Stocks", "market": "United States", "universe": "US Mega Caps", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "US_SPY", "symbol": "SPY", "name": "S&P 500 ETF", "asset_class": "ETFs", "market": "United States", "universe": "US Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "US_QQQ", "symbol": "QQQ", "name": "Nasdaq-100 ETF", "asset_class": "ETFs", "market": "United States", "universe": "US Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_SPX500", "symbol": "SPX500/USD", "name": "S&P 500 reference index", "asset_class": "Indices", "market": "United States", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_NAS100", "symbol": "NAS100/USD", "name": "Nasdaq-100 reference index", "asset_class": "Indices", "market": "United States", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_US30", "symbol": "US30/USD", "name": "Dow Jones 30 reference index", "asset_class": "Indices", "market": "United States", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_US2000", "symbol": "US2000/USD", "name": "Russell 2000 reference index", "asset_class": "Indices", "market": "United States", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_DE30", "symbol": "DE30/EUR", "name": "DAX reference index", "asset_class": "Indices", "market": "Germany", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_UK100", "symbol": "UK100/GBP", "name": "FTSE 100 reference index", "asset_class": "Indices", "market": "United Kingdom", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "IDX_JP225", "symbol": "JP225/USD", "name": "Nikkei 225 reference index", "asset_class": "Indices", "market": "Japan", "universe": "Major Indices", "timeframe": "1d", "horizon": 5},
    {"instrument_id": "FX_EURUSD", "symbol": "EUR/USD", "name": "Euro / US Dollar", "asset_class": "Forex", "market": "Majors", "universe": "Major Pairs", "timeframe": "1h", "horizon": 5},
    {"instrument_id": "FX_GBPUSD", "symbol": "GBP/USD", "name": "British Pound / US Dollar", "asset_class": "Forex", "market": "Majors", "universe": "Major Pairs", "timeframe": "1h", "horizon": 5},
    {"instrument_id": "FX_USDJPY", "symbol": "USD/JPY", "name": "US Dollar / Japanese Yen", "asset_class": "Forex", "market": "Majors", "universe": "Major Pairs", "timeframe": "1h", "horizon": 5},
    {"instrument_id": "CMD_GOLD", "symbol": "XAU/USD", "name": "Gold", "asset_class": "Commodities", "market": "Metals", "universe": "Precious Metals", "timeframe": "4h", "horizon": 5},
    {"instrument_id": "CRYPTO_BTC", "symbol": "BTC/USD", "name": "Bitcoin", "asset_class": "Crypto", "market": "Large Cap", "universe": "Core Crypto", "timeframe": "1h", "horizon": 5},
    {"instrument_id": "CRYPTO_ETH", "symbol": "ETH/USD", "name": "Ethereum", "asset_class": "Crypto", "market": "Large Cap", "universe": "Core Crypto", "timeframe": "1h", "horizon": 5},
)


def universe() -> list[dict]:
    return [dict(item) for item in APPROVED_TRAINING_UNIVERSE]


def _asset_class(row: dict) -> str | None:
    category = str(row.get("category") or "").strip()
    dataset = str(row.get("dataset") or "").strip().lower()
    aliases = {
        "stocks": "Stocks", "stock": "Stocks", "etfs": "ETFs", "etf": "ETFs",
        "indices": "Indices", "index": "Indices", "forex": "Forex", "fx": "Forex",
        "crypto": "Crypto", "cryptocurrency": "Crypto", "commodities": "Commodities",
        "commodity": "Commodities", "futures": "Futures", "future": "Futures",
    }
    return aliases.get(category.lower()) or aliases.get(dataset)


def _market_name(value: object) -> str:
    raw = str(value or "Global").strip() or "Global"
    return {"GLOBAL": "Global", "GG": "Guernsey", "JE": "Jersey"}.get(raw, raw)


@lru_cache(maxsize=1)
def global_training_catalog() -> tuple[dict, ...]:
    try:
        rows = json.loads(CATALOG_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        rows = []
    result: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        asset_class = _asset_class(row)
        symbol = str(row.get("symbol") or "").strip()
        name = str(row.get("name") or symbol).strip()
        if asset_class not in SUPPORTED_ASSET_CLASSES or not symbol:
            continue
        key = (asset_class, symbol)
        if key in seen:
            continue
        seen.add(key)
        dataset = str(row.get("dataset") or "market").strip().lower()
        result.append({
            "instrument_id": f"lse:{dataset}:{symbol}",
            "symbol": symbol,
            "name": name,
            "asset_class": asset_class,
            "market": _market_name(row.get("country")),
            "universe": "London Strategic Edge global catalog",
            "dataset": dataset,
            "timeframe": DEFAULT_TIMEFRAMES[asset_class],
            "horizon": 5,
        })
    return tuple(result)


def search_training_catalog(*, asset_class: str | None = None, market: str | None = None,
                            query: str = "", limit: int = 500) -> dict:
    matching_class = [
        dict(item) for item in global_training_catalog()
        if not asset_class or item["asset_class"] == asset_class
    ]
    markets = sorted({item["market"] for item in matching_class})
    query_lower = query.strip().lower()
    filtered = [
        item for item in matching_class
        if (not market or item["market"] == market)
        and (not query_lower or query_lower in f"{item['symbol']} {item['name']} {item['market']}".lower())
    ]
    return {
        "instruments": filtered[:max(1, min(limit, 1000))],
        "markets": markets,
        "matched": len(filtered),
        "catalog_total": len(global_training_catalog()),
    }


def catalog_training_keys() -> set[tuple[str, str, int]]:
    return {
        (item["symbol"], item["timeframe"], int(item["horizon"]))
        for item in global_training_catalog()
    }


def catalog_training_symbols() -> set[str]:
    """Return canonical symbols approved for research training.

    Timeframe and prediction horizon are experiment settings, so they must not
    be confused with the catalog defaults used to populate the UI.
    """
    return {item["symbol"] for item in global_training_catalog()}


def catalog_asset_classes() -> dict[str, str]:
    return {item["symbol"]: item["asset_class"] for item in global_training_catalog()}
