from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path("/Users/macmac/Documents/Codex/FX")
RUNTIME_CATALOG_PATH = ROOT / "data" / "runtime" / "lse_catalog.json"
SEED_CATALOG_PATH = ROOT / "data" / "catalog" / "lse_catalog.json"
SUPPORTED_ASSET_CLASSES = ("Stocks", "ETFs", "Indices", "Forex", "Commodities", "Crypto", "Futures")
DEFAULT_TIMEFRAMES = {
    "Stocks": "1d", "ETFs": "1d", "Indices": "1d", "Futures": "1d",
    "Forex": "1h", "Crypto": "1h", "Commodities": "4h",
}

GLOBAL_CORE_SYMBOLS = (
    # Global equities: United States, Europe, Japan, South Korea, United Kingdom and Australia.
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "JPM",
    "XOM", "NKE", "SAP", "ASML", "7203.T", "005930.KS", "SHEL", "BHP",
    # Diversified and thematic exchange-traded funds.
    "SPY", "QQQ", "IWM", "EEM", "GLD",
    # Regional equity indices.
    "SPX500/USD", "NAS100/USD", "DE30/EUR", "UK100/GBP", "EU50/EUR",
    "HK33/HKD", "JP225/USD", "AU200/AUD",
    # Liquid global currency pairs.
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "AUD/USD", "USD/CHF",
    # Metals and energy commodities.
    "XAU/USD", "XAG/USD", "WTICO/USD", "BCO/USD", "XCU/USD",
    # Large-cap crypto markets.
    "BTC/USD", "ETH/USD", "XRP/USD", "SOL/USD", "BNB/USD", "ADA/USD",
    # Major index and metal futures.
    "ES.F", "NQ.F", "GC.F", "SI.F",
)

# Curated from the owner's research brief. This keeps day-to-day selectors useful
# without hiding the full catalog from explicit research workflows.
FOCUSED_SYMBOLS_BY_CLASS = {
    "Stocks": (
        # Image list and global companies that exist in the verified LSE catalog.
        "0700.HK", "1398.HK", "SAP", "005930.KS", "BABA", "0939.HK", "ASML",
        "0941.HK", "3988.HK", "AZN", "NVS", "LIN", "HSBC", "RELIANCE.NS", "SHEL",
        "0857.HK", "NVO", "CBA.AX", "RY", "1810.HK", "PDD", "ACN", "UL", "ETN",
        "2318.HK", "BHARTIARTL.NS", "BHP", "PG", "V", "JNJ", "GOOGL", "GOOG", "AAPL",
        "UAA", "UA", "BKNG", "ABNB", "MSFT", "WWW", "COST", "MA", "SBUX", "MCD",
        "ADP", "JPM", "HD", "CNI", "WM", "ALLY", "CAT", "PEP", "ITW", "KO",
        # Berkshire and disclosed U.S. portfolio names.
        "AXP", "BAC", "COF", "CVX", "DHI", "DVA", "DAL", "JEF", "KHC", "KR", "LEN",
        "LEN.B", "LLYVA", "LLYVK", "LPX", "M", "MCO", "NVR", "NYT", "NUE", "OXY",
        "SIRI", "VRSN", "CB", "DJT", "OBDC", "OWL", "BX", "NVDA", "AVGO", "ORCL",
        "DELL", "AMZN", "PLTR", "ABT", "ABBV", "MO", "AVB", "BDX", "BLK", "BF.B",
        "CSCO", "CFG", "CMCSA", "STZ", "IBM", "KVUE", "KMI", "LMT", "MRK", "MS",
        "NEE", "NKE", "OMC", "PH", "PFE", "PM", "PPG", "PSA", "ROK", "RTX", "TXN",
        "TMO", "TFC", "VZ", "WMT", "WSO", "WEC", "ZTS", "APO", "ANET", "T", "ADSK",
        "AZO", "AXON", "BJ", "XYZ", "BA", "BAH", "BMY", "NFLX", "NEM", "NSC", "NOC",
        "NRG", "ORLY", "OKTA", "OKE", "OTIS", "OVV",
        # Additional liquid global research names from the owner's brief.
        "RACE", "SPOT", "SHOP", "MELI", "SE", "3690.HK", "BIDU", "LI", "8035.T",
        "6857.T", "6861.T", "6098.T", "9983.T", "7974.T", "RIO", "TTE", "E", "EQNR",
        "NGG", "SAN", "BBVA", "SNY", "CP", "BN", "CNQ", "CCJ", "B",
        # Explicit owner requests retained alongside the research brief.
        "TSLA", "XOM", "META",
    ),
    "ETFs": ("SPY", "QQQ", "IWM", "GLD", "EEM", "VOO", "DIA", "XLE", "XLF", "TLT"),
    "Indices": (
        "SPX500/USD", "NAS100/USD", "US30/USD", "DE30/EUR", "UK100/GBP",
        "EU50/EUR", "JP225/USD", "HK33/HKD", "AU200/AUD",
    ),
    "Forex": (
        "EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "USD/CAD",
        "USD/CHF", "NZD/USD", "EUR/JPY", "GBP/JPY", "EUR/GBP",
    ),
    "Commodities": (
        "XAU/USD", "XAG/USD", "WTICO/USD", "BCO/USD", "NATGAS/USD",
        "XCU/USD", "XPT/USD", "SOYBN/USD", "CORN/USD", "COFFEE/USD",
    ),
    "Crypto": (
        "BTC/USD", "ETH/USD", "BNB/USD", "XRP/USD", "SOL/USD",
        "TRX/USD", "LINK/USD", "DOGE/USD", "ADA/USD",
    ),
    "Futures": ("ES.F", "NQ.F", "GC.F", "SI.F", "FDAX.F", "FESX.F"),
}


def universe() -> list[dict]:
    """Return a bounded global research universe plus every enabled Favorite.

    The full catalog remains available for one-off/batch experiments. Continuously
    training thousands of instruments would waste compute and multiply-test the
    same weak hypotheses, so autopilot uses the owner's verified focused catalog
    plus Favorites, capped by ``FX_GLOBAL_TRAINING_LIMIT`` (256 by default).
    """
    catalog = {item["symbol"]: dict(item) for item in global_training_catalog()}
    selected: list[dict] = []
    seen: set[str] = set()

    try:
        from services.operations.store import list_favorites
        favorites = [item for item in list_favorites() if item.get("enabled")]
    except Exception:
        favorites = []

    for favorite in favorites:
        symbol = str(favorite.get("symbol") or "")
        base = catalog.get(symbol)
        if not base or symbol in seen:
            continue
        base.update({
            "instrument_id": favorite.get("instrument_id") or base["instrument_id"],
            "timeframe": favorite.get("execution_timeframe") or base["timeframe"],
            "horizon": 5,
            "universe": "Enabled Favorites",
        })
        selected.append(base)
        seen.add(symbol)

    for symbol in GLOBAL_CORE_SYMBOLS:
        base = catalog.get(symbol)
        if not base or symbol in seen:
            continue
        base["universe"] = "Approved Global Core"
        selected.append(base)
        seen.add(symbol)

    for asset_class in SUPPORTED_ASSET_CLASSES:
        for symbol in FOCUSED_SYMBOLS_BY_CLASS.get(asset_class, ()):
            base = catalog.get(symbol)
            if not base or symbol in seen:
                continue
            base["universe"] = "Verified Focused Research"
            selected.append(base)
            seen.add(symbol)

    limit = max(1, int(os.getenv("FX_GLOBAL_TRAINING_LIMIT", "256")))
    return selected[:limit]



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
        catalog_path = RUNTIME_CATALOG_PATH if RUNTIME_CATALOG_PATH.exists() else SEED_CATALOG_PATH
        rows = json.loads(catalog_path.read_text())
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
                            query: str = "", limit: int = 500, focused: bool = False) -> dict:
    focused_symbols = {
        symbol for group, symbols in FOCUSED_SYMBOLS_BY_CLASS.items()
        if not asset_class or group == asset_class for symbol in symbols
    }
    matching_class = [
        dict(item) for item in global_training_catalog()
        if not asset_class or item["asset_class"] == asset_class
        if not focused or item["symbol"] in focused_symbols
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
        "focused": focused,
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
