import os

from alpaca.trading.client import (
    TradingClient,
)

from alpaca.trading.enums import (
    OrderClass,
    OrderSide,
    TimeInForce,
)

from alpaca.trading.requests import (
    MarketOrderRequest,
    StopLossRequest,
    TakeProfitRequest,
)


class AlpacaPaperBroker:

    """
    PAPER ONLY.

    paper=True is intentionally hard-coded.

    This class cannot connect to Alpaca live trading.
    """

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
                "Your Alpaca Paper connection is missing."
            )

        self.client = TradingClient(
            key,
            secret,
            paper=True,
        )

    def account(self):

        return self.client.get_account()

    def positions(self):

        return self.client.get_all_positions()

    def submit_long_bracket(
        self,
        symbol: str,
        qty: int,
        take_profit: float,
        stop_loss: float,
    ):

        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=(
                TimeInForce.DAY
            ),
            order_class=(
                OrderClass.BRACKET
            ),
            take_profit=(
                TakeProfitRequest(
                    limit_price=round(
                        take_profit,
                        2,
                    )
                )
            ),
            stop_loss=(
                StopLossRequest(
                    stop_price=round(
                        stop_loss,
                        2,
                    )
                )
            ),
        )

        return self.client.submit_order(
            order_data=request
        )
