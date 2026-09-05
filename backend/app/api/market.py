from fastapi import APIRouter

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)


router = APIRouter(
    prefix="/api/market",
    tags=["market"],
)


ALIASES = {
    "XAUUSD": "XAU/USD",
    "GOLD": "XAU/USD",
    "BTCUSD": "BTC/USD",
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
}


@router.get("/{symbol}/chart")
async def chart_data(
    symbol: str,
):

    requested = (
        symbol
        .upper()
        .strip()
    )

    lse_symbol = ALIASES.get(
        requested,
        requested,
    )

    try:

        service = (
            LSEGlobalMarketData()
        )

        rows = service.candles(
            symbol=lse_symbol,
            timeframe="1d",
            limit=180,
        )

        if not rows:

            return {
                "available": False,
                "symbol": lse_symbol,
                "message": (
                    "London Strategic Edge did not return enough market history."
                ),
                "bars": [],
            }

        latest = rows[-1]

        bars = []

        for row in rows:

            bars.append({
                "time": (
                    row.get("timestamp")
                    or row.get("time")
                    or row.get("ts")
                ),
                "open": (
                    row.get("open")
                    or row.get("o")
                ),
                "high": (
                    row.get("high")
                    or row.get("h")
                ),
                "low": (
                    row.get("low")
                    or row.get("l")
                ),
                "close": (
                    row.get("close")
                    or row.get("c")
                ),
                "volume": (
                    row.get("volume")
                    or row.get("v")
                    or 0
                ),
            })

        return {
            "available": True,
            "symbol": lse_symbol,
            "source": (
                "London Strategic Edge"
            ),
            "latest_price": (
                latest.get("close")
                or latest.get("c")
            ),
            "bars": bars,
        }

    except Exception:

        return {
            "available": False,
            "symbol": lse_symbol,
            "message": (
                "FX could not retrieve this market from London Strategic Edge right now."
            ),
            "bars": [],
        }
