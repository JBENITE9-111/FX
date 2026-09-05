from __future__ import annotations

import json
import math
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path("/Users/macmac/Documents/Codex/FX")
DB_PATH = ROOT / "data" / "paper_fleet" / "fleet.sqlite3"
STATE_PATH = ROOT / "data" / "paper_fleet" / "latest.json"

STRATEGIES = [
    "Trend Following",
    "Momentum",
    "20-Period Breakout",
    "Mean Reversion",
    "Bollinger Mean Reversion",
    "RSI Reversion",
    "MACD Trend",
    "Volatility Breakout",
    "Kalman Trend",
    "Pairs Trading",
    "Cross-Sectional Momentum",
    "Regime-Aware Trend",
    "Carry",
    "Institutional Positioning",
    "Activist Event",
    "Options Volatility",
]

@dataclass
class StrategySnapshot:
    strategy: str
    status: str
    capital_assigned: float
    nav: float
    signal: int
    signal_name: str
    symbol: str
    data_source: str
    last_price: float | None
    position_units: float
    realized_pnl: float
    unrealized_pnl: float
    observations: int
    signal_changes: int
    updated_at: float
    note: str

def _initial_capital() -> float:
    return float(
        os.getenv(
            "FX_PAPER_FLEET_CAPITAL_PER_STRATEGY",
            "1.00",
        )
    )

def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_state (
            strategy TEXT PRIMARY KEY,
            nav REAL NOT NULL,
            cash REAL NOT NULL,
            position_units REAL NOT NULL,
            position_side INTEGER NOT NULL,
            entry_price REAL,
            realized_pnl REAL NOT NULL,
            observations INTEGER NOT NULL,
            signal_changes INTEGER NOT NULL,
            last_signal INTEGER NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            timestamp REAL NOT NULL,
            symbol TEXT NOT NULL,
            price REAL,
            signal INTEGER NOT NULL,
            nav REAL NOT NULL,
            realized_pnl REAL NOT NULL,
            unrealized_pnl REAL NOT NULL,
            note TEXT
        )
        """
    )

    return conn

def _load_prices(symbol: str) -> tuple[pd.DataFrame, str]:
    """
    Paper-fleet fallback market feed.

    The main FX app continues to use London Strategic Edge as primary research.
    This micro-paper heartbeat uses Yahoo Finance only as a fallback until the
    existing LSE history adapter is wired directly into this worker.
    """
    frame = yf.download(
        symbol,
        period="6mo",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if frame.empty:
        raise RuntimeError(f"No market data for {symbol}")

    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [column[0] for column in frame.columns]

    frame = frame.dropna()

    if len(frame) < 40:
        raise RuntimeError(f"Not enough history for {symbol}")

    return frame, "Yahoo Finance fallback for micro-paper fleet"

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def _signal(name: str, frame: pd.DataFrame) -> tuple[int, str]:
    close = frame["Close"].astype(float)
    high = frame["High"].astype(float)
    low = frame["Low"].astype(float)
    last = float(close.iloc[-1])

    ema20 = close.ewm(span=20, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    returns = close.pct_change()

    if name == "Trend Following":
        return (
            1 if ema20.iloc[-1] > ema50.iloc[-1] else -1,
            "EMA20 vs EMA50",
        )

    if name == "Momentum":
        momentum = close.iloc[-1] / close.iloc[-21] - 1
        return (
            1 if momentum > 0 else -1,
            "20-day momentum",
        )

    if name == "20-Period Breakout":
        prev_high = high.shift(1).rolling(20).max().iloc[-1]
        prev_low = low.shift(1).rolling(20).min().iloc[-1]

        if last > prev_high:
            return 1, "20-day upside breakout"

        if last < prev_low:
            return -1, "20-day downside breakout"

        return 0, "No breakout"

    if name == "Mean Reversion":
        mean = close.rolling(20).mean().iloc[-1]
        std = close.rolling(20).std().iloc[-1]
        z = ((last - mean) / std) if std and not math.isnan(std) else 0

        if z < -1:
            return 1, f"z={z:.2f}"

        if z > 1:
            return -1, f"z={z:.2f}"

        return 0, f"z={z:.2f}"

    if name == "Bollinger Mean Reversion":
        mean = close.rolling(20).mean().iloc[-1]
        std = close.rolling(20).std().iloc[-1]

        if last < mean - 2 * std:
            return 1, "Below lower Bollinger band"

        if last > mean + 2 * std:
            return -1, "Above upper Bollinger band"

        return 0, "Inside Bollinger bands"

    if name == "RSI Reversion":
        value = float(_rsi(close).iloc[-1])

        if value < 30:
            return 1, f"RSI={value:.1f}"

        if value > 70:
            return -1, f"RSI={value:.1f}"

        return 0, f"RSI={value:.1f}"

    if name == "MACD Trend":
        fast = close.ewm(span=12, adjust=False).mean()
        slow = close.ewm(span=26, adjust=False).mean()
        macd = fast - slow
        signal_line = macd.ewm(span=9, adjust=False).mean()

        return (
            1 if macd.iloc[-1] > signal_line.iloc[-1] else -1,
            "MACD vs signal",
        )

    if name == "Volatility Breakout":
        atr = (high - low).rolling(14).mean()
        range_now = high.iloc[-1] - low.iloc[-1]

        if range_now > 1.5 * atr.iloc[-1]:
            return (
                1 if close.iloc[-1] > close.iloc[-2] else -1,
                "Volatility expansion",
            )

        return 0, "No volatility breakout"

    if name == "Kalman Trend":
        smooth = close.ewm(span=10, adjust=False).mean()
        return (
            1 if smooth.iloc[-1] > smooth.iloc[-5] else -1,
            "Smoothed-trend proxy until existing FX Kalman adapter is linked",
        )

    if name == "Regime-Aware Trend":
        vol = returns.rolling(20).std().iloc[-1]
        median_vol = float(returns.rolling(20).std().dropna().median())

        if vol > 2 * median_vol:
            return 0, "Extreme volatility regime"

        return (
            1 if ema20.iloc[-1] > ema50.iloc[-1] else -1,
            "Trend allowed by volatility regime",
        )

    specialized = {
        "Pairs Trading": "Running; waiting for validated pair adapter",
        "Cross-Sectional Momentum": "Running; waiting for validated universe adapter",
        "Carry": "Running; waiting for FX/futures funding adapter",
        "Institutional Positioning": "Running; waiting for institutional/COT adapter",
        "Activist Event": "Running; waiting for validated activist-event feed",
        "Options Volatility": "Running; waiting for options IV surface adapter",
    }

    return 0, specialized.get(name, "NO_TRADE")

def _load_state(conn, strategy: str) -> dict:
    row = conn.execute(
        """
        SELECT nav,cash,position_units,position_side,entry_price,
               realized_pnl,observations,signal_changes,last_signal
        FROM strategy_state WHERE strategy=?
        """,
        (strategy,),
    ).fetchone()

    if row:
        return {
            "nav": float(row[0]),
            "cash": float(row[1]),
            "position_units": float(row[2]),
            "position_side": int(row[3]),
            "entry_price": float(row[4]) if row[4] is not None else None,
            "realized_pnl": float(row[5]),
            "observations": int(row[6]),
            "signal_changes": int(row[7]),
            "last_signal": int(row[8]),
        }

    capital = _initial_capital()

    return {
        "nav": capital,
        "cash": capital,
        "position_units": 0.0,
        "position_side": 0,
        "entry_price": None,
        "realized_pnl": 0.0,
        "observations": 0,
        "signal_changes": 0,
        "last_signal": 0,
    }

def run_cycle(symbol: str | None = None) -> dict:
    symbol = symbol or os.getenv(
        "FX_PAPER_FLEET_DEFAULT_SYMBOL",
        "AAPL",
    )

    frame, data_source = _load_prices(symbol)
    price = float(frame["Close"].iloc[-1])
    now = time.time()
    conn = _connect()
    snapshots = []

    try:
        for strategy in STRATEGIES:
            signal, note = _signal(strategy, frame)
            state = _load_state(conn, strategy)
            state["observations"] += 1
            old_signal = state["last_signal"]

            if signal != old_signal:
                state["signal_changes"] += 1

                if state["position_side"] != 0 and state["entry_price"]:
                    pnl = (
                        state["position_units"]
                        * (price - state["entry_price"])
                        * state["position_side"]
                    )
                    state["realized_pnl"] += pnl
                    state["cash"] += pnl

                state["position_units"] = 0.0
                state["position_side"] = 0
                state["entry_price"] = None

                if signal in (-1, 1):
                    capital = max(0.0, state["cash"])
                    state["position_units"] = (
                        capital / price
                        if price > 0
                        else 0.0
                    )
                    state["position_side"] = signal
                    state["entry_price"] = price

                state["last_signal"] = signal

            unrealized = 0.0

            if state["position_side"] != 0 and state["entry_price"]:
                unrealized = (
                    state["position_units"]
                    * (price - state["entry_price"])
                    * state["position_side"]
                )

            nav = state["cash"] + unrealized

            conn.execute(
                """
                INSERT INTO strategy_state(
                    strategy,nav,cash,position_units,position_side,
                    entry_price,realized_pnl,observations,signal_changes,
                    last_signal,updated_at
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(strategy) DO UPDATE SET
                    nav=excluded.nav,
                    cash=excluded.cash,
                    position_units=excluded.position_units,
                    position_side=excluded.position_side,
                    entry_price=excluded.entry_price,
                    realized_pnl=excluded.realized_pnl,
                    observations=excluded.observations,
                    signal_changes=excluded.signal_changes,
                    last_signal=excluded.last_signal,
                    updated_at=excluded.updated_at
                """,
                (
                    strategy,
                    nav,
                    state["cash"],
                    state["position_units"],
                    state["position_side"],
                    state["entry_price"],
                    state["realized_pnl"],
                    state["observations"],
                    state["signal_changes"],
                    state["last_signal"],
                    now,
                ),
            )

            conn.execute(
                """
                INSERT INTO strategy_history(
                    strategy,timestamp,symbol,price,signal,nav,
                    realized_pnl,unrealized_pnl,note
                )
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    strategy,
                    now,
                    symbol,
                    price,
                    signal,
                    nav,
                    state["realized_pnl"],
                    unrealized,
                    note,
                ),
            )

            snapshots.append(
                StrategySnapshot(
                    strategy=strategy,
                    status="RUNNING",
                    capital_assigned=_initial_capital(),
                    nav=round(nav, 8),
                    signal=signal,
                    signal_name={
                        -1: "SHORT",
                        0: "NO_TRADE",
                        1: "LONG",
                    }[signal],
                    symbol=symbol,
                    data_source=data_source,
                    last_price=price,
                    position_units=round(
                        state["position_units"],
                        10,
                    ),
                    realized_pnl=round(
                        state["realized_pnl"],
                        8,
                    ),
                    unrealized_pnl=round(
                        unrealized,
                        8,
                    ),
                    observations=state["observations"],
                    signal_changes=state["signal_changes"],
                    updated_at=now,
                    note=note,
                )
            )

        conn.commit()
    finally:
        conn.close()

    payload = {
        "generated_at": now,
        "mode": "VIRTUAL_PAPER_MICRO",
        "real_money": False,
        "paper_capital_per_strategy": _initial_capital(),
        "symbol": symbol,
        "strategies": [asdict(item) for item in snapshots],
        "policy": (
            "Every strategy worker runs every cycle and has $1 virtual paper capital. "
            "FX never manufactures a trade solely to keep capital moving. "
            "NO_TRADE is part of the system."
        ),
    }

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp, STATE_PATH)

    return payload

def load_latest() -> dict:
    if not STATE_PATH.exists():
        return run_cycle()

    return json.loads(
        STATE_PATH.read_text(
            encoding="utf-8"
        )
    )
