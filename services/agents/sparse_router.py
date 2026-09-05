from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Expert:
    expert_id: str
    tags: frozenset[str]
    sovereign: bool = False

EXPERTS = [
    Expert("macro", frozenset({"macro", "rates", "fx", "bonds", "economy", "geopolitics"})),
    Expert("trend", frozenset({"trend", "momentum", "structure", "breakout"})),
    Expert("mean_reversion", frozenset({"mean_reversion", "range", "rsi", "bollinger"})),
    Expert("volatility", frozenset({"volatility", "options", "atr", "iv"})),
    Expert("order_flow", frozenset({"order_flow", "liquidity", "volume", "microstructure"})),
    Expert("crypto", frozenset({"crypto", "funding", "open_interest", "btc", "tokenomics"})),
    Expert("fundamentals", frozenset({"stocks", "fundamentals", "earnings", "valuation"})),
    Expert("fraud_counter_thesis", frozenset({"fraud", "counter_thesis", "bias", "overfitting"})),
    Expert("execution", frozenset({"execution", "slippage", "spread", "broker", "orders"})),
    Expert("risk", frozenset({"risk", "portfolio", "correlation", "drawdown"}), sovereign=True),
]

def route(tags: set[str], top_k: int | None = None) -> list[str]:
    """
    Sparse expert routing inspired by MoE architectures.

    Risk remains sovereign and is NOT replaced by expert voting.
    """
    top_k = top_k or int(os.getenv("FX_SPARSE_EXPERTS_PER_STAGE", "2"))

    scored = []
    for expert in EXPERTS:
        if expert.sovereign:
            continue
        score = len(tags & expert.tags)
        if score > 0:
            scored.append((score, expert.expert_id))

    scored.sort(reverse=True)

    selected = [expert_id for _, expert_id in scored[:top_k]]

    if not selected:
        selected = ["trend", "macro"][:top_k]

    return selected
