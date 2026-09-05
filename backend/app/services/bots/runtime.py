from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)

from backend.app.services.strategies.backtester import (
    backtest,
)


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

STATE_FILE = (
    ROOT
    / "data"
    / "bots"
    / "runtime.json"
)


DEFAULT_BOTS = {
    "global_equity": {
        "id": "global_equity",
        "name": "Global Equity Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "trend_following",
        "timeframe": "1d",
        "watchlist": [
            "AAPL",
            "NVDA",
            "MSFT",
            "AMZN",
            "META",
            "GOOGL",
            "TSLA",
            "SPY",
            "QQQ",
        ],
        "scan_every_seconds": 300,
    },

    "forex": {
        "id": "forex",
        "name": "Forex Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "trend_following",
        "timeframe": "1h",
        "watchlist": [
            "EUR/USD",
            "GBP/USD",
            "USD/JPY",
            "EUR/JPY",
            "GBP/JPY",
            "AUD/USD",
            "USD/CAD",
            "USD/CHF",
        ],
        "scan_every_seconds": 300,
    },

    "crypto": {
        "id": "crypto",
        "name": "Crypto Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "momentum",
        "timeframe": "1h",
        "watchlist": [
            "BTC/USD",
            "ETH/USD",
        ],
        "scan_every_seconds": 300,
    },

    "gold": {
        "id": "gold",
        "name": "Gold Bot",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "kalman_trend",
        "timeframe": "4h",
        "watchlist": [
            "XAU/USD",
        ],
        "scan_every_seconds": 300,
    },

    "commodities": {
        "id": "commodities",
        "name": "Commodities Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "kalman_trend",
        "timeframe": "4h",
        "watchlist": ["XAU/USD", "XAG/USD", "XPT/USD", "WTICO/USD", "BCO/USD", "XCU/USD", "NATGAS/USD"],
        "scan_every_seconds": 300,
    },

    "indices": {
        "id": "indices",
        "name": "Global Indices Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "trend_following",
        "timeframe": "1d",
        "watchlist": ["SPX500/USD", "NAS100/USD", "US30/USD", "US2000/USD", "DE30/EUR", "UK100/GBP", "JP225/USD"],
        "scan_every_seconds": 300,
    },

    "etfs": {
        "id": "etfs",
        "name": "ETF Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "trend_following",
        "timeframe": "1d",
        "watchlist": ["SPY", "QQQ", "IWM", "DIA", "GLD", "SLV", "XLE"],
        "scan_every_seconds": 300,
    },

    "futures": {
        "id": "futures",
        "name": "Futures Research Scanner",
        "mode": "WATCH",
        "status": "STOPPED",
        "strategy": "trend_following",
        "timeframe": "1d",
        "watchlist": ["ES.F", "NQ.F", "GC.F", "SI.F", "FDAX", "FESX"],
        "scan_every_seconds": 300,
    },
}


class BotRuntime:

    def __init__(self):

        self.tasks: dict[
            str,
            asyncio.Task
        ] = {}

        self.state = (
            self._load()
        )

    def _load(self):

        if STATE_FILE.exists():

            try:

                stored = json.loads(
                    STATE_FILE.read_text()
                )

            except Exception:

                stored = {}

        else:

            stored = {}

        result = {}

        for (
            bot_id,
            config
        ) in DEFAULT_BOTS.items():

            merged = dict(
                config
            )

            merged.update(
                stored.get(
                    bot_id,
                    {},
                )
            )

            # Never silently continue an automated process
            # after the server is restarted.
            merged[
                "status"
            ] = "STOPPED"

            result[
                bot_id
            ] = merged

        self._save(
            result
        )

        return result

    def _save(
        self,
        state=None,
    ):

        if state is None:

            state = self.state

        STATE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        STATE_FILE.write_text(
            json.dumps(
                state,
                indent=2,
                default=str,
            )
        )

    def list(self):

        return [
            {
                **bot,
                "data_source": "London Strategic Edge OHLCV price history",
                "runtime_location": "Local FX backend process on this Mac",
                "activity": "Fetch candles, run a deterministic historical strategy test, and record watch-only candidates",
                "learns_while_scanning": False,
                "can_place_orders": False,
            }
            for bot in self.state.values()
        ]

    def get(
        self,
        bot_id,
    ):

        return self.state.get(
            bot_id
        )

    def configure(
        self,
        bot_id: str,
        changes: dict[str, Any],
    ):

        bot = self.state.get(
            bot_id
        )

        if not bot:

            raise ValueError(
                "FX could not find this bot."
            )

        allowed = {
            "mode",
            "watchlist",
            "strategy",
            "timeframe",
            "scan_every_seconds",
        }

        for (
            key,
            value
        ) in changes.items():

            if key in allowed:

                bot[
                    key
                ] = value

        self._save()

        return bot

    async def scan_once(
        self,
        bot_id: str,
    ):

        bot = self.state[
            bot_id
        ]

        service = (
            LSEGlobalMarketData()
        )

        results = []

        for symbol in bot[
            "watchlist"
        ]:

            try:

                rows = await asyncio.to_thread(
                    service.candles,
                    symbol,
                    bot[
                        "timeframe"
                    ],
                    500,
                )

                analysis = await asyncio.to_thread(
                    backtest,
                    bot[
                        "strategy"
                    ],
                    rows,
                )

                latest = rows[-1]

                latest_price = (
                    latest.get(
                        "close"
                    )
                    or latest.get(
                        "c"
                    )
                )

                results.append({
                    "symbol":
                        symbol,

                    "price":
                        latest_price,

                    "current_position":
                        analysis[
                            "current_position"
                        ],

                    "historical_return":
                        analysis[
                            "total_return"
                        ],

                    "max_drawdown":
                        analysis[
                            "max_drawdown"
                        ],

                    "win_rate":
                        analysis[
                            "win_rate"
                        ],

                    "sharpe":
                        analysis[
                            "sharpe"
                        ],
                })

            except Exception as exc:

                results.append({
                    "symbol": symbol,
                    "error": str(exc),
                })

        candidates = [
            x
            for x in results
            if (
                x.get(
                    "current_position"
                )
                == 1
            )
        ]

        candidates.sort(
            key=lambda x:
                (
                    x.get(
                        "sharpe"
                    )
                    if x.get(
                        "sharpe"
                    )
                    is not None
                    else -999
                ),
            reverse=True,
        )

        bot[
            "last_scan"
        ] = time.time()

        bot[
            "last_results"
        ] = results

        bot[
            "candidates"
        ] = candidates[:10]

        self._save()

        return bot

    async def _loop(
        self,
        bot_id,
    ):

        bot = self.state[
            bot_id
        ]

        while (
            bot[
                "status"
            ]
            == "RUNNING"
        ):

            try:

                await self.scan_once(
                    bot_id
                )

            except Exception as exc:

                bot[
                    "last_error"
                ] = str(exc)

                self._save()

            await asyncio.sleep(
                max(
                    int(
                        bot.get(
                            "scan_every_seconds",
                            300,
                        )
                    ),
                    60,
                )
            )

    def start(
        self,
        bot_id,
    ):

        bot = self.state.get(
            bot_id
        )

        if not bot:

            raise ValueError(
                "FX could not find this bot."
            )

        existing = self.tasks.get(
            bot_id
        )

        if (
            existing
            and not existing.done()
        ):

            return bot

        bot[
            "status"
        ] = "RUNNING"

        self._save()

        task = asyncio.create_task(
            self._loop(
                bot_id
            )
        )

        self.tasks[
            bot_id
        ] = task

        return bot

    def stop(
        self,
        bot_id,
    ):

        bot = self.state.get(
            bot_id
        )

        if not bot:

            raise ValueError(
                "FX could not find this bot."
            )

        bot[
            "status"
        ] = "STOPPED"

        task = self.tasks.get(
            bot_id
        )

        if task:

            task.cancel()

        self._save()

        return bot


bots = BotRuntime()
