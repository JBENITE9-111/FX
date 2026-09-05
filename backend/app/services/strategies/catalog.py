STRATEGIES = [
    {
        "id": "trend_following",
        "name": "Trend Following",
        "family": "Trend",
        "plain_english": (
            "Attempts to stay with a market that is already moving consistently in one direction."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "momentum",
        "name": "Momentum",
        "family": "Momentum",
        "plain_english": (
            "Looks for markets where recent movement is strong enough that it may continue."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "breakout",
        "name": "20-Period Breakout",
        "family": "Breakout",
        "plain_english": (
            "Looks for price moving beyond a range that contained the market recently."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "mean_reversion",
        "name": "Mean Reversion",
        "family": "Mean Reversion",
        "plain_english": (
            "Looks for unusually stretched prices that might move back toward their recent average."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "bollinger_reversion",
        "name": "Bollinger Mean Reversion",
        "family": "Mean Reversion",
        "plain_english": (
            "Measures whether price has moved unusually far away from its recent average."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "rsi_reversion",
        "name": "RSI Reversion",
        "family": "Mean Reversion",
        "plain_english": (
            "Looks for very strong short-term buying or selling that may have become excessive."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "macd_trend",
        "name": "MACD Trend",
        "family": "Trend",
        "plain_english": (
            "Compares faster and slower price trends to identify changes in direction."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "volatility_breakout",
        "name": "Volatility Breakout",
        "family": "Breakout",
        "plain_english": (
            "Looks for a strong directional move occurring while market movement is expanding."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "kalman_trend",
        "name": "Kalman Trend",
        "family": "Statistical",
        "plain_english": (
            "Filters out some price noise and follows the estimated underlying trend."
        ),
        "required_data": [
            "OHLC",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "pairs",
        "name": "Pairs Trading",
        "family": "Statistical Arbitrage",
        "plain_english": (
            "Looks for two historically related markets moving unusually far apart."
        ),
        "required_data": [
            "Two instruments",
        ],
        "status": "RESEARCH · PAIR REQUIRED",
    },
    {
        "id": "cross_sectional_momentum",
        "name": "Cross-Sectional Momentum",
        "family": "Momentum",
        "plain_english": (
            "Ranks many markets and compares the strongest against the weakest."
        ),
        "required_data": [
            "Market universe",
        ],
        "status": "RESEARCH · UNIVERSE REQUIRED",
    },
    {
        "id": "regime_trend",
        "name": "Regime-Aware Trend",
        "family": "Regime",
        "plain_english": (
            "Allows trend strategies only when the detected market environment is suitable."
        ),
        "required_data": [
            "OHLC",
            "Regime model",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "carry",
        "name": "Carry",
        "family": "Macro",
        "plain_english": (
            "Studies return opportunities associated with yield, funding or futures-curve differences."
        ),
        "required_data": [
            "Rates or futures curves",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "institutional_positioning",
        "name": "Institutional Positioning",
        "family": "Positioning",
        "plain_english": (
            "Uses regulatory positioning information as context for crowded or changing institutional exposure."
        ),
        "required_data": [
            "CFTC / regulatory positioning",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "activist_event",
        "name": "Activist Event",
        "family": "Event",
        "plain_english": (
            "Studies market behavior around significant activist ownership disclosures."
        ),
        "required_data": [
            "SEC Schedule 13D / 13G",
        ],
        "status": "RESEARCH",
    },
    {
        "id": "options_volatility",
        "name": "Options Volatility",
        "family": "Volatility",
        "plain_english": (
            "Compares options-implied expectations with realized market movement."
        ),
        "required_data": [
            "Options",
            "Spot price",
        ],
        "status": "RESEARCH",
    },
]
