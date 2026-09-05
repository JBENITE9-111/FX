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


        order = submit_market_order(
            instrument=instrument,

            asset_class="research",

            side=direction,

            price=float(
                price
            ),

            notional=notional,

            strategy_id=strategy,

            bot_id="strategy_fleet",

            metadata={
                "source":
                    "FX Paper Strategy Fleet",

                "mode":
                    "LOCAL_PAPER_AUTO",
            },
        )


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
