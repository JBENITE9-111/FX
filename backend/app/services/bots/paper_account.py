from __future__ import annotations

from backend.app.services.brokers.alpaca_paper import (
    AlpacaPaperBroker,
)


def paper_snapshot():

    broker = AlpacaPaperBroker()

    account = broker.account()

    try:

        positions = (
            broker.positions()
        )

    except Exception:

        positions = []

    start_equity = float(
        getattr(
            account,
            "last_equity",
            account.equity,
        )
        or account.equity
    )

    equity = float(
        account.equity
    )

    cash = float(
        account.cash
    )

    buying_power = float(
        account.buying_power
    )

    day_pnl = (
        equity
        - start_equity
    )

    position_rows = []

    for position in positions:

        position_rows.append({
            "symbol":
                position.symbol,

            "quantity":
                float(
                    position.qty
                ),

            "market_value":
                float(
                    position.market_value
                ),

            "average_entry":
                float(
                    position.avg_entry_price
                ),

            "current_price":
                float(
                    position.current_price
                ),

            "unrealized_pnl":
                float(
                    position.unrealized_pl
                ),

            "unrealized_percent":
                float(
                    position.unrealized_plpc
                )
                * 100,
        })

    return {
        "mode": "PAPER",
        "broker": "Alpaca Paper",
        "equity": equity,
        "cash": cash,
        "buying_power": buying_power,
        "day_pnl": day_pnl,
        "positions": position_rows,
        "real_money": False,
    }
