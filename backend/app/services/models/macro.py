from __future__ import annotations

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)


class MacroContextEngine:

    MARKETS = {
        "US Stocks": "SPY",
        "Euro / Dollar": "EUR/USD",
        "Gold": "XAU/USD",
        "Bitcoin": "BTC/USD",
    }

    def snapshot(
        self,
        timeframe: str = "1d",
    ):

        service = (
            LSEGlobalMarketData()
        )

        result = {}

        for name, symbol in (
            self.MARKETS.items()
        ):

            try:

                rows = service.candles(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=30,
                )

                closes = [
                    float(
                        row.get(
                            "close",
                            row.get(
                                "c"
                            )
                        )
                    )
                    for row in rows
                    if (
                        row.get(
                            "close",
                            row.get(
                                "c"
                            )
                        )
                        is not None
                    )
                ]

                if len(closes) >= 21:

                    change = (
                        closes[-1]
                        / closes[-21]
                        - 1
                    )

                    result[name] = {
                        "symbol": symbol,
                        "price": closes[-1],
                        "20_period_change": change,
                    }

            except Exception:

                continue

        return {
            "source": (
                "London Strategic Edge"
            ),
            "markets": result,
            "important": (
                "This cross-market view is context, not an automatic trading signal."
            ),
        }
