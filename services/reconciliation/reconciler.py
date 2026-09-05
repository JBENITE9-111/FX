from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReconciliationResult:
    status: str
    mismatches: list[dict[str, Any]] = field(default_factory=list)

    @property
    def trading_allowed(self) -> bool:
        return self.status == "PASS"


def reconcile_position_maps(
    internal: dict[str, float],
    broker: dict[str, float],
    *,
    tolerance: float = 1e-9,
) -> ReconciliationResult:

    mismatches = []

    symbols = set(internal) | set(broker)

    for symbol in sorted(symbols):
        internal_qty = float(internal.get(symbol, 0.0))
        broker_qty = float(broker.get(symbol, 0.0))

        if abs(internal_qty - broker_qty) > tolerance:
            mismatches.append(
                {
                    "instrument": symbol,
                    "internal_quantity": internal_qty,
                    "broker_quantity": broker_qty,
                }
            )

    return ReconciliationResult(
        status="PASS" if not mismatches else "BLOCK",
        mismatches=mismatches,
    )
