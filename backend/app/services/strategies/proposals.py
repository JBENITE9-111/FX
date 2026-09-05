from __future__ import annotations

import json
import math
import os
import uuid

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path

from backend.app.services.brokers.alpaca_paper import (
    AlpacaPaperBroker,
)

from backend.app.services.models.features import (
    calculate_features,
)

from backend.app.services.strategies.backtester import (
    backtest,
)


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

STORE = (
    ROOT
    / "data"
    / "trade_proposals"
    / "proposals.json"
)


def load_store():

    if not STORE.exists():

        return {}

    try:

        return json.loads(
            STORE.read_text()
        )

    except Exception:

        return {}


def save_store(
    data,
):

    STORE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    STORE.write_text(
        json.dumps(
            data,
            indent=2,
            default=str,
        )
    )


def create_paper_proposal(
    strategy_id: str,
    symbol: str,
    rows,
):

    if "/" in symbol:

        raise ValueError(
            "Automatic Paper execution is currently enabled only for Alpaca-supported US stock symbols."
        )

    results = backtest(
        strategy_id,
        rows,
    )

    direction = results[
        "current_position"
    ]

    if direction != 1:

        raise ValueError(
            "This strategy does not currently have a long entry signal. FX will not force a trade."
        )

    features = calculate_features(
        rows
    )

    entry = features[
        "last_price"
    ]

    atr = features[
        "atr14"
    ]

    if (
        entry is None
        or atr is None
        or atr <= 0
    ):

        raise ValueError(
            "FX cannot calculate a safe Paper proposal from the available data."
        )

    stop = (
        entry
        - 2 * atr
    )

    target = (
        entry
        + 4 * atr
    )

    broker = (
        AlpacaPaperBroker()
    )

    account = broker.account()

    equity = float(
        account.equity
    )

    risk_pct = float(
        os.getenv(
            "PAPER_RISK_PER_TRADE_PCT",
            "0.25",
        )
    ) / 100

    max_notional_pct = float(
        os.getenv(
            "PAPER_MAX_NOTIONAL_PCT",
            "5.0",
        )
    ) / 100

    risk_budget = (
        equity
        * risk_pct
    )

    max_notional = (
        equity
        * max_notional_pct
    )

    per_share_risk = (
        entry
        - stop
    )

    qty_by_risk = math.floor(
        risk_budget
        / per_share_risk
    )

    qty_by_notional = math.floor(
        max_notional
        / entry
    )

    qty = max(
        min(
            qty_by_risk,
            qty_by_notional,
        ),
        0,
    )

    if qty < 1:

        raise ValueError(
            "The Paper risk limits do not permit even one share for this proposal."
        )

    proposal_id = str(
        uuid.uuid4()
    )

    proposal = {
        "id": proposal_id,
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "status": (
            "PENDING_APPROVAL"
        ),
        "mode": "PAPER",
        "symbol": symbol,
        "strategy_id": strategy_id,
        "side": "BUY",
        "quantity": qty,
        "reference_entry": entry,
        "stop_loss": stop,
        "take_profit": target,
        "planned_risk_dollars": (
            per_share_risk
            * qty
        ),
        "maximum_notional": (
            entry
            * qty
        ),
        "data_source": (
            "London Strategic Edge"
        ),
        "broker": (
            "Alpaca Paper"
        ),
        "backtest": results,
        "real_money": False,
    }

    store = load_store()

    store[
        proposal_id
    ] = proposal

    save_store(
        store
    )

    return proposal


def approve_paper_proposal(
    proposal_id: str,
):

    store = load_store()

    proposal = store.get(
        proposal_id
    )

    if not proposal:

        raise ValueError(
            "FX could not find this Paper trade proposal."
        )

    if (
        proposal["status"]
        != "PENDING_APPROVAL"
    ):

        raise ValueError(
            "This proposal has already been processed."
        )

    if proposal[
        "mode"
    ] != "PAPER":

        raise RuntimeError(
            "Only Paper Trading proposals can be executed by this service."
        )

    broker = (
        AlpacaPaperBroker()
    )

    order = (
        broker.submit_long_bracket(
            symbol=proposal[
                "symbol"
            ],
            qty=int(
                proposal[
                    "quantity"
                ]
            ),
            take_profit=float(
                proposal[
                    "take_profit"
                ]
            ),
            stop_loss=float(
                proposal[
                    "stop_loss"
                ]
            ),
        )
    )

    proposal[
        "status"
    ] = "SUBMITTED_TO_ALPACA_PAPER"

    proposal[
        "broker_order_id"
    ] = str(
        order.id
    )

    proposal[
        "approved_at"
    ] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    store[
        proposal_id
    ] = proposal

    save_store(
        store
    )

    return proposal
