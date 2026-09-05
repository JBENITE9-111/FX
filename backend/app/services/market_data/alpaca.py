import os
from datetime import datetime, timedelta, timezone

from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    StockLatestTradeRequest,
)
from alpaca.data.timeframe import TimeFrame


class AlpacaMarketData:

    def __init__(self):

        key = os.getenv(
            "ALPACA_PAPER_KEY",
            "",
        )

        secret = os.getenv(
            "ALPACA_PAPER_SECRET",
            "",
        )

        if not key or not secret:
            raise RuntimeError(
                "Your Alpaca Paper connection is not configured."
            )

        self.client = StockHistoricalDataClient(
            key,
            secret,
        )

    def daily_bars(
        self,
        symbol: str,
        days: int = 180,
    ):

        end = datetime.now(
            timezone.utc
        ) - timedelta(
            minutes=20
        )

        start = end - timedelta(
            days=days
        )

        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,
            start=start,
            end=end,

            # Alpaca's free real-time stock feed.
            feed=DataFeed.IEX,
        )

        return self.client.get_stock_bars(
            request
        )

    def latest_trade(
        self,
        symbol: str,
    ):

        request = StockLatestTradeRequest(
            symbol_or_symbols=[symbol],

            # Explicitly use the free IEX feed.
            feed=DataFeed.IEX,
        )

        return self.client.get_stock_latest_trade(
            request
        )
