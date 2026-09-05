BOTS = [
    {
        "id": "global_scanner",
        "name": "Global Scanner Bot",
        "markets": "Global LSE universe",
        "strategy": (
            "Multi-strategy screening"
        ),
        "timeframe": "Multiple",
        "mode": "RESEARCH",
        "status": "RESEARCH_ONLY",
        "availability_reason": "No exact instrument/timeframe model has passed the promotion gates.",
        "requires_approval": True,
    },

    {
        "id": "btc_momentum",
        "name": "Bitcoin Momentum Bot",
        "markets": "BTC/USD",
        "strategy": (
            "Momentum + Trend"
        ),
        "timeframe": "1H",
        "mode": "RESEARCH",
        "status": "RESEARCH_ONLY",
        "availability_reason": "No calibrated 85% trade probability or passed walk-forward model is registered.",
        "requires_approval": True,
    },

    {
        "id": "gold_trend",
        "name": "Gold Trend Bot",
        "markets": "XAU/USD",
        "strategy": (
            "Trend + Macro Context"
        ),
        "timeframe": "4H",
        "mode": "RESEARCH",
        "status": "RESEARCH_ONLY",
        "availability_reason": "Gold research exists, but the execution qualification evidence is incomplete.",
        "requires_approval": True,
    },

    {
        "id": "us_stock_trend",
        "name": "US Stock Trend Bot",
        "markets": (
            "US stocks"
        ),
        "strategy": (
            "Trend + Momentum + Council"
        ),
        "timeframe": "1D",
        "mode": "RESEARCH",
        "status": "RESEARCH_ONLY",
        "availability_reason": "Research scans are not evidence of paper-execution qualification.",
        "requires_approval": True,
    },
]
