from __future__ import annotations

import json
import os

from pathlib import Path

from services.local_paper.broker import (
    positions,
    submit_market_order,
)


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

FLEET = (
    ROOT
    / "data"
    / "paper_fleet"
    / "latest.json"
)


def existing_strategy_keys():

    result = set()

    for position in positions():

        result.add(
            (
                position.get(
                    "strategy_id"
                )
                or "",

                position.get(
                    "instrument"
                )
                or "",

                position.get(
                    "side_name"
                )
                or "",
            )
        )

    return result


def run():

    if (
        os.getenv(
            "FX_LOCAL_PAPER_AUTO_BOTS",
            "true",
        )
        .lower()
        != "true"
    ):

        return {
            "status":
                "DISABLED"
        }


    if not FLEET.exists():

        return {
            "status":
                "WAITING",

            "reason":
                "Paper strategy fleet has no data yet.",
        }


    fleet = json.loads(
        FLEET.read_text()
    )


    notional = float(
        os.getenv(
            "FX_LOCAL_PAPER_BOT_NOTIONAL",
            "100",
        )
    )


    existing = (
        existing_strategy_keys()
    )


    opened = []

    skipped = []


    for item in fleet.get(
        "strategies",
        [],
    ):

        strategy = item[
            "strategy"
        ]

        instrument = item[
            "symbol"
        ]

        direction = item[
            "signal_name"
        ]

        price = item.get(
            "last_price"
        )


        if direction == "NO_TRADE":

            skipped.append(
                {
                    "strategy":
                        strategy,

                    "reason":
                        "NO_TRADE",
                }
            )

            continue

        # This legacy fleet emits research observations, not calibrated and
        # protected trade plans. It therefore cannot execute directly.
        if item.get("eligibility") != "PAPER_ELIGIBLE":
            skipped.append({
                "strategy": strategy,
                "reason": "research signal is not qualified for protected paper execution",
            })
            continue

        required_trade_plan = {
            "signal_id": item.get("signal_id"),
            "asset_class": item.get("asset_class"),
            "stop": item.get("stop"),
            "structural_invalidation": item.get("structural_invalidation"),
            "profit_plan": item.get("profit_plan"),
            "maximum_loss": item.get("maximum_loss"),
        }
        missing_trade_plan = [
            field
            for field, value in required_trade_plan.items()
            if value is None or (isinstance(value, str) and not value.strip())
        ]
        if missing_trade_plan:
            skipped.append({
                "strategy": strategy,
                "reason": (
                    "PAPER_ELIGIBLE signal is missing protected execution fields: "
                    + ", ".join(missing_trade_plan)
                ),
            })
            continue

        try:
            stop = float(required_trade_plan["stop"])
            structural_invalidation = float(
                required_trade_plan["structural_invalidation"]
            )
            maximum_loss = float(required_trade_plan["maximum_loss"])
            if maximum_loss <= 0:
                raise ValueError("maximum_loss must be positive")
        except (TypeError, ValueError) as exc:
            skipped.append({
                "strategy": strategy,
                "reason": f"invalid protected execution plan: {exc}",
            })
            continue


        side_name = (
            "LONG"
            if direction == "LONG"
            else "SHORT"
        )


        key = (
            strategy,
            instrument,
            side_name,
        )


        if key in existing:

            skipped.append(
                {
                    "strategy":
                        strategy,

                    "reason":
                        "position already open",
                }
            )

            continue


        if not price:

            skipped.append(
                {
                    "strategy":
                        strategy,

                    "reason":
                        "no price",
                }
            )

            continue


        try:
            order = submit_market_order(
                instrument=instrument,

                asset_class=str(required_trade_plan["asset_class"]),

                side=direction,

                price=float(
                    price
                ),

                notional=notional,

                strategy_id=strategy,

                bot_id="strategy_fleet",

                signal_id=str(required_trade_plan["signal_id"]),

                stop=stop,

                structural_invalidation=structural_invalidation,

                profit_plan=str(required_trade_plan["profit_plan"]),

                maximum_loss=maximum_loss,

                strategy_version=str(item.get("strategy_version") or "1"),

                metadata={
                    "source":
                        "FX Paper Strategy Fleet",

                    "mode":
                        "LOCAL_PAPER_AUTO",

                    "data_source": item.get("data_source"),
                },
            )
        except (TypeError, ValueError) as exc:
            skipped.append({
                "strategy": strategy,
                "reason": f"protected paper broker rejected signal: {exc}",
            })
            continue


        opened.append(
            order.__dict__
        )


    return {
        "status":
            "COMPLETE",

        "opened":
            opened,

        "skipped":
            skipped,

        "paper_only":
            True,
    }
