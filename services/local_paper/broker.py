from __future__ import annotations

import json
import math
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager

from dataclasses import (
    asdict,
    dataclass,
)

from pathlib import Path

from typing import Any, Iterator


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

DB_PATH = ROOT / os.getenv(
    "FX_LOCAL_PAPER_DB",
    "data/local_paper/local_paper.sqlite3",
)


@dataclass
class PaperOrder:

    order_id: str

    instrument: str

    asset_class: str

    side: str

    quantity: float

    price: float

    notional: float

    strategy_id: str | None

    bot_id: str | None

    signal_id: str | None

    status: str

    created_at: float


def get_order_by_signal(signal_id: str | None) -> PaperOrder | None:
    if not signal_id:
        return None
    with _connect() as conn:
        row = conn.execute("SELECT * FROM orders WHERE signal_id=?", (signal_id,)).fetchone()
    if not row:
        return None
    item = dict(row)
    return PaperOrder(
        order_id=item["order_id"], instrument=item["instrument"],
        asset_class=item["asset_class"], side=item["side"],
        quantity=float(item["quantity"]), price=float(item["price"]),
        notional=float(item["notional"]), strategy_id=item["strategy_id"] or None,
        bot_id=item["bot_id"] or None, signal_id=item["signal_id"],
        status=item["status"], created_at=float(item["created_at"]),
    )


def _starting_cash() -> float:

    return float(
        os.getenv(
            "FX_LOCAL_PAPER_STARTING_CASH",
            "100000",
        )
    )


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY CHECK(id=1),
            starting_cash REAL NOT NULL,
            cash REAL NOT NULL,
            realized_pnl REAL NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS protection_plans (
            plan_id TEXT PRIMARY KEY,
            instrument TEXT NOT NULL,
            asset_class TEXT NOT NULL,
            direction TEXT NOT NULL,
            entry REAL NOT NULL,
            notional REAL NOT NULL,
            quantity REAL NOT NULL,
            timeframe TEXT NOT NULL,
            market_data_timestamp TEXT NOT NULL,
            strategy_id TEXT NOT NULL,
            bot_id TEXT NOT NULL,
            plan_version TEXT NOT NULL,
            plan_json TEXT NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS positions (
            position_id TEXT PRIMARY KEY,

            instrument TEXT NOT NULL,
            asset_class TEXT NOT NULL,

            strategy_id TEXT,
            bot_id TEXT,

            side INTEGER NOT NULL,

            quantity REAL NOT NULL,

            average_price REAL NOT NULL,

            last_price REAL NOT NULL,

            realized_pnl REAL NOT NULL,

            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,

            trade_id TEXT,
            campaign_id TEXT,
            stop REAL,
            structural_invalidation REAL,
            profit_plan TEXT,
            maximum_loss REAL,
            strategy_version TEXT,
            owner_id TEXT NOT NULL DEFAULT 'local-owner',
            legacy INTEGER NOT NULL DEFAULT 0,

            UNIQUE(
                instrument,
                strategy_id,
                bot_id
            )
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,

            instrument TEXT NOT NULL,
            asset_class TEXT NOT NULL,

            side TEXT NOT NULL,

            quantity REAL NOT NULL,
            price REAL NOT NULL,
            notional REAL NOT NULL,

            strategy_id TEXT,
            bot_id TEXT,
            signal_id TEXT,

            status TEXT NOT NULL,

            created_at REAL NOT NULL,

            metadata_json TEXT
        )
        """
    )

    # Migrate databases created by earlier FX builds without discarding history.
    existing_position_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(positions)")
    }
    for name, definition in {
        "trade_id": "TEXT", "campaign_id": "TEXT", "stop": "REAL",
        "structural_invalidation": "REAL", "profit_plan": "TEXT",
        "maximum_loss": "REAL", "strategy_version": "TEXT",
        "owner_id": "TEXT NOT NULL DEFAULT 'local-owner'",
        "legacy": "INTEGER NOT NULL DEFAULT 1",
        "protection_plan_id": "TEXT",
        "protection_plan_json": "TEXT",
        "plan_state_json": "TEXT",
        "initial_quantity": "REAL",
        "last_evaluated_bar": "TEXT",
    }.items():
        if name not in existing_position_columns:
            conn.execute(f"ALTER TABLE positions ADD COLUMN {name} {definition}")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS equity_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp REAL NOT NULL,

            cash REAL NOT NULL,

            equity REAL NOT NULL,

            unrealized_pnl REAL NOT NULL,

            realized_pnl REAL NOT NULL
        )
        """
    )

    conn.execute(
        """CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_signal_id
           ON orders(signal_id) WHERE signal_id IS NOT NULL AND signal_id <> ''"""
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS training_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp REAL NOT NULL,

            instrument TEXT NOT NULL,

            strategy_id TEXT,
            bot_id TEXT,

            event_type TEXT NOT NULL,

            payload_json TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            trade_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL,
            account_id TEXT NOT NULL DEFAULT 'local-paper', campaign_id TEXT,
            bot_id TEXT NOT NULL, strategy_id TEXT NOT NULL,
            strategy_version TEXT NOT NULL, instrument TEXT NOT NULL,
            asset_class TEXT NOT NULL, exposure_class TEXT NOT NULL,
            mode TEXT NOT NULL DEFAULT 'LOCAL_PAPER', direction TEXT NOT NULL,
            quantity REAL NOT NULL, entry_price REAL NOT NULL, exit_price REAL,
            stop REAL NOT NULL, structural_invalidation REAL NOT NULL,
            profit_plan TEXT NOT NULL, maximum_loss REAL NOT NULL,
            gross_pnl REAL, net_pnl REAL, opened_at REAL NOT NULL,
            closed_at REAL, last_exit_at REAL, exit_reason TEXT, status TEXT NOT NULL,
            legacy INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    existing_trade_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(trades)")
    }
    for name, definition in {
        "protection_plan_id": "TEXT",
        "protection_plan_json": "TEXT",
        "last_exit_at": "REAL",
    }.items():
        if name not in existing_trade_columns:
            conn.execute(f"ALTER TABLE trades ADD COLUMN {name} {definition}")

    row = conn.execute(
        """
        SELECT id
        FROM account
        WHERE id=1
        """
    ).fetchone()

    if not row:

        now = time.time()

        cash = _starting_cash()

        conn.execute(
            """
            INSERT INTO account(
                id,
                starting_cash,
                cash,
                realized_pnl,
                created_at,
                updated_at
            )
            VALUES(
                1,?,?,?,?,?
            )
            """,
            (
                cash,
                cash,
                0.0,
                now,
                now,
            ),
        )

    conn.commit()

    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _position_key(
    instrument: str,
    strategy_id: str | None,
    bot_id: str | None,
):

    return (
        instrument,
        strategy_id or "",
        bot_id or "",
    )


def record_training_event(
    *,
    instrument: str,
    strategy_id: str | None,
    bot_id: str | None,
    event_type: str,
    payload: dict[str, Any],
) -> None:

    with _connect() as conn:

        conn.execute(
            """
            INSERT INTO training_events(
                timestamp,
                instrument,
                strategy_id,
                bot_id,
                event_type,
                payload_json
            )
            VALUES(
                ?,?,?,?,?,?
            )
            """,
            (
                time.time(),
                instrument,
                strategy_id,
                bot_id,
                event_type,
                json.dumps(
                    payload,
                    default=str,
                ),
            ),
        )


def create_protection_plan(plan: dict[str, Any], *, ttl_seconds: int = 300) -> dict[str, Any]:
    """Persist a generated paper-only plan with a unique single-use identity."""
    now = time.time()
    plan_id = "paper-plan-" + uuid.uuid4().hex
    record = {**plan, "plan_id": plan_id, "created_at": now, "expires_at": now + ttl_seconds}
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO protection_plans(
                plan_id,instrument,asset_class,direction,entry,notional,quantity,
                timeframe,market_data_timestamp,strategy_id,bot_id,plan_version,
                plan_json,created_at,expires_at,status
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                plan_id, plan["instrument"], plan["asset_class"], plan["direction"],
                plan["entry"], plan["notional"], plan["quantity"], plan["timeframe"],
                plan["market_data_timestamp"], plan["strategy_id"], plan["bot_id"],
                plan["plan_version"], json.dumps(record, sort_keys=True), now,
                now + ttl_seconds, "ACTIVE",
            ),
        )
    return record


def get_protection_plan(plan_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM protection_plans WHERE plan_id=?", (plan_id,)
        ).fetchone()
    if not row:
        return None
    record = json.loads(row["plan_json"])
    record["status"] = row["status"]
    # Expiry and lifecycle status are authoritative database state. Keeping them
    # outside the immutable payload lets expiry/consumption be updated safely.
    record["created_at"] = float(row["created_at"])
    record["expires_at"] = float(row["expires_at"])
    return record


def consume_protection_plan(plan_id: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE protection_plans SET status='CONSUMED' WHERE plan_id=? AND status='ACTIVE'",
            (plan_id,),
        )


def validate_protection_plan(
    plan_id: str,
    *,
    instrument: str,
    asset_class: str,
    direction: str,
    entry: float,
    notional: float,
    strategy_id: str,
    bot_id: str,
) -> dict[str, Any]:
    plan = get_protection_plan(plan_id)
    if not plan or plan.get("status") != "ACTIVE":
        raise ValueError("The selected protection plan is unavailable. Recalculate it.")
    if time.time() > float(plan["expires_at"]):
        raise ValueError("The selected protection plan expired. Recalculate it from current market data.")
    expected = (
        str(plan["instrument"]).upper(), plan["asset_class"], plan["direction"],
        plan["strategy_id"], plan["bot_id"],
    )
    actual = (instrument.upper(), asset_class, direction, strategy_id, bot_id)
    if expected != actual:
        raise ValueError("The protection plan does not match this instrument, direction, strategy, or bot.")
    entry_tolerance = max(abs(float(plan["entry"])) * 0.001, float(plan["atr_14"]) * 0.10)
    if abs(float(entry) - float(plan["entry"])) > entry_tolerance:
        raise ValueError("The entry moved materially since this plan was calculated. Recalculate it.")
    if abs(float(notional) - float(plan["notional"])) > max(0.01, float(plan["notional"]) * 0.001):
        raise ValueError("The protection plan does not match the current paper notional.")
    return plan


def local_risk_capacity() -> dict[str, float]:
    account = get_account()
    equity = max(0.0, float(account["equity"]))
    per_trade_pct = float(os.getenv("PAPER_RISK_PER_TRADE_PCT", "0.25"))
    per_trade = equity * per_trade_pct / 100
    portfolio_limit = equity * float(os.getenv("FX_LOCAL_PAPER_MAX_OPEN_RISK_PCT", "3.0")) / 100
    daily_limit = equity * float(os.getenv("FX_LOCAL_PAPER_DAILY_LOSS_LIMIT_PCT", "2.0")) / 100
    day_start = time.time() - (time.time() % 86400)
    with _connect() as conn:
        open_risk = float(conn.execute(
            "SELECT COALESCE(SUM(maximum_loss),0) FROM positions"
        ).fetchone()[0])
        daily_net = float(conn.execute(
            "SELECT COALESCE(SUM(net_pnl),0) FROM trades WHERE last_exit_at>=?", (day_start,)
        ).fetchone()[0])
    remaining_portfolio = max(0.0, portfolio_limit - open_risk)
    remaining_daily = max(0.0, daily_limit + min(0.0, daily_net))
    return {
        "equity": equity,
        "total_exposure": float(account["total_exposure"]),
        "per_trade_risk_cap": per_trade,
        "per_trade_risk_pct": per_trade_pct,
        "portfolio_risk_limit": portfolio_limit,
        "open_planned_risk": open_risk,
        "remaining_portfolio_risk": remaining_portfolio,
        "daily_loss_limit": daily_limit,
        "daily_realized_pnl": daily_net,
        "remaining_daily_loss_capacity": remaining_daily,
        "effective_new_trade_risk_cap": min(per_trade, remaining_portfolio, remaining_daily),
    }


def get_account() -> dict:

    with _connect() as conn:

        account = dict(
            conn.execute(
                """
                SELECT *
                FROM account
                WHERE id=1
                """
            ).fetchone()
        )

        positions = [
            dict(row)
            for row
            in conn.execute(
                """
                SELECT *
                FROM positions
                ORDER BY updated_at DESC
                """
            ).fetchall()
        ]

    unrealized = 0.0
    short_unrealized = 0.0
    long_market_value = 0.0

    exposure = 0.0

    for position in positions:

        direction = int(
            position["side"]
        )

        qty = float(
            position["quantity"]
        )

        entry = float(
            position["average_price"]
        )

        last = float(
            position["last_price"]
        )

        unrealized += (
            qty
            * (
                last - entry
            )
            * direction
        )

        if direction == 1:
            long_market_value += qty * last
        else:
            short_unrealized += qty * (last - entry) * direction

        exposure += abs(
            qty
            * last
        )

    equity = (
        float(
            account["cash"]
        )
        + long_market_value
        + short_unrealized
    )

    return {
        **account,

        "equity":
            equity,

        "unrealized_pnl":
            unrealized,

        "total_exposure":
            exposure,

        "positions":
            len(positions),
    }


def positions() -> list[dict]:

    with _connect() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM positions
            ORDER BY updated_at DESC
            """
        ).fetchall()

    result = []

    for row in rows:

        item = dict(row)

        direction = int(
            item["side"]
        )

        quantity = float(
            item["quantity"]
        )

        entry = float(
            item["average_price"]
        )

        last = float(
            item["last_price"]
        )

        item[
            "side_name"
        ] = (
            "LONG"
            if direction == 1
            else "SHORT"
        )

        item[
            "market_value"
        ] = abs(
            quantity
            * last
        )

        item[
            "unrealized_pnl"
        ] = (
            quantity
            * (
                last
                - entry
            )
            * direction
        )

        result.append(
            item
        )

    return result


def protect_legacy_positions() -> int:
    """Attach a conservative, explicit plan to positions from pre-safety builds.

    The levels are derived from each position's latest stored market mark.  This
    migration does not open, close, or resize anything; it only removes naked
    paper exposure from records created before protection fields existed.
    """
    updated = 0
    now = time.time()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT position_id, side, quantity, average_price, last_price
            FROM positions
            WHERE stop IS NULL
               OR structural_invalidation IS NULL
               OR profit_plan IS NULL
               OR TRIM(profit_plan) = ''
               OR maximum_loss IS NULL
               OR (side=1 AND stop>=average_price)
               OR (side=-1 AND stop<=average_price)
            """
        ).fetchall()
        for row in rows:
            mark = float(row["last_price"])
            quantity = abs(float(row["quantity"]))
            direction = 1 if int(row["side"]) == 1 else -1
            risk_per_unit = max(mark * 0.02, 0.000001)
            stop = mark - direction * risk_per_unit
            target_1 = mark + direction * risk_per_unit
            target_2 = mark + direction * risk_per_unit * 2.0
            plan = json.dumps(
                {
                    "type": "MIGRATED_SCALE_1R_2R",
                    "target_1": target_1,
                    "target_2": target_2,
                    "basis": "latest stored market mark at safety migration",
                },
                sort_keys=True,
            )
            conn.execute(
                """
                UPDATE positions
                SET stop=?, structural_invalidation=?, profit_plan=?,
                    maximum_loss=?, strategy_version=COALESCE(strategy_version, 'legacy-1'),
                    legacy=1, plan_state_json=?, last_evaluated_bar=NULL, updated_at=?
                WHERE position_id=?
                """,
                (
                    stop,
                    stop,
                    plan,
                    quantity * risk_per_unit,
                    json.dumps({
                        "status": "AWAITING_REVIEW",
                        "target_1_filled": False,
                        "trail_active": False,
                    }, sort_keys=True),
                    now,
                    row["position_id"],
                ),
            )
            updated += 1
        conn.commit()
    return updated


def submit_market_order(
    *,
    instrument: str,
    asset_class: str,
    side: str,
    price: float,
    quantity: float | None = None,
    notional: float | None = None,
    strategy_id: str | None = None,
    bot_id: str | None = None,
    signal_id: str | None = None,
    metadata: dict | None = None,
    stop: float | None = None,
    structural_invalidation: float | None = None,
    profit_plan: str | None = None,
    maximum_loss: float | None = None,
    campaign_id: str | None = None,
    strategy_version: str = "1",
    owner_id: str = "local-owner",
    reduce_only: bool = False,
    protection_plan_id: str | None = None,
    protection_plan: dict[str, Any] | None = None,
) -> PaperOrder:

    # A signal is the stable idempotency key for retryable execution requests.
    existing_order = get_order_by_signal(signal_id)
    if existing_order:
        return existing_order

    if price <= 0:

        raise ValueError(
            "Price must be positive."
        )

    side = (
        side
        .strip()
        .upper()
    )

    if side not in {
        "BUY",
        "SELL",
        "LONG",
        "SHORT",
    }:

        raise ValueError(
            "Side must be BUY/SELL/LONG/SHORT."
        )

    direction = (
        1
        if side
        in {
            "BUY",
            "LONG",
        }
        else -1
    )

    matching_position = next(
        (
            position
            for position in positions()
            if position["instrument"] == instrument
            and (position.get("strategy_id") or "") == (strategy_id or "")
            and (position.get("bot_id") or "") == (bot_id or "")
        ),
        None,
    )
    reducing = bool(
        matching_position
        and int(matching_position["side"]) != direction
    )

    if matching_position and not reducing:
        raise ValueError(
            "Adding to an open position is disabled; manage or close the existing trade first."
        )

    if reduce_only and not reducing:
        raise ValueError("A reduce-only order cannot increase or reverse exposure.")

    if not reducing:
        if not strategy_id or not bot_id:
            raise ValueError("A new paper position requires bot and strategy identifiers.")
        if stop is None or structural_invalidation is None or not str(profit_plan or "").strip():
            raise ValueError(
                "A new paper position requires structural invalidation, stop loss, and profit plan."
            )
        if maximum_loss is None or maximum_loss <= 0:
            raise ValueError("A new paper position requires a positive maximum loss.")
        if (direction == 1 and stop >= price) or (direction == -1 and stop <= price):
            raise ValueError("The protective stop is on the wrong side of the entry.")

    if quantity is None:

        if (
            notional is None
            or notional <= 0
        ):

            raise ValueError(
                "Provide quantity or notional."
            )

        quantity = (
            float(
                notional
            )
            / price
        )

    quantity = abs(
        float(
            quantity
        )
    )

    if not reducing:
        planned_loss_at_stop = quantity * abs(price - float(stop))
        if planned_loss_at_stop > float(maximum_loss) + 1e-9:
            raise ValueError(
                "Position size risks more at the protective stop than the stated maximum loss."
            )
        capacity = local_risk_capacity()
        if float(maximum_loss) > capacity["effective_new_trade_risk_cap"] + 1e-9:
            raise ValueError(
                "The planned maximum loss exceeds the remaining per-trade, daily, or portfolio risk capacity."
            )

    order_notional = (
        quantity
        * price
    )

    max_position = float(
        os.getenv(
            "FX_LOCAL_PAPER_MAX_POSITION_NOTIONAL",
            "1000",
        )
    )

    if (
        not reducing
        and
        max_position > 0
        and order_notional
        > max_position
    ):

        raise ValueError(
            f"Paper order exceeds local "
            f"position limit ${max_position:,.2f}."
        )

    account = get_account()

    max_total = float(
        os.getenv(
            "FX_LOCAL_PAPER_MAX_TOTAL_EXPOSURE",
            "10000",
        )
    )

    if (
        not reducing
        and
        max_total > 0
        and (
            account[
                "total_exposure"
            ]
            + order_notional
        )
        > max_total
    ):

        raise ValueError(
            "Local paper portfolio exposure limit exceeded."
        )

    if (
        not reducing
        and
        direction == 1
        and order_notional
        > float(
            account["cash"]
        )
    ):

        raise ValueError(
            "Not enough virtual cash."
        )

    now = time.time()

    order_id = str(
        uuid.uuid4()
    )

    strategy_db = (
        strategy_id
        or ""
    )

    bot_db = (
        bot_id
        or ""
    )

    with _connect() as conn:

        current = conn.execute(
            """
            SELECT *
            FROM positions

            WHERE
                instrument=?
                AND strategy_id=?
                AND bot_id=?
            """,
            (
                instrument,
                strategy_db,
                bot_db,
            ),
        ).fetchone()

        cash_change = 0.0

        realized_delta = 0.0

        if current is None:

            position_id = str(
                uuid.uuid4()
            )
            trade_id = str(uuid.uuid4())

            conn.execute(
                """
                INSERT INTO positions(
                    position_id,
                    instrument,
                    asset_class,
                    strategy_id,
                    bot_id,
                    side,
                    quantity,
                    average_price,
                    last_price,
                    realized_pnl,
                    created_at,
                    updated_at,
                    trade_id,
                    campaign_id,
                    stop,
                    structural_invalidation,
                    profit_plan,
                    maximum_loss,
                    strategy_version,
                    owner_id,
                    legacy,
                    protection_plan_id,
                    protection_plan_json,
                    plan_state_json,
                    initial_quantity,
                    last_evaluated_bar
                )
                VALUES(
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )
                """,
                (
                    position_id,
                    instrument,
                    asset_class,
                    strategy_db,
                    bot_db,
                    direction,
                    quantity,
                    price,
                    price,
                    0.0,
                    now,
                    now,
                    trade_id,
                    campaign_id,
                    stop,
                    structural_invalidation,
                    profit_plan,
                    maximum_loss,
                    strategy_version,
                    owner_id,
                    0,
                    protection_plan_id,
                    json.dumps(protection_plan, sort_keys=True) if protection_plan else None,
                    json.dumps({"status": "ARMED", "target_1_filled": False, "trail_active": False}),
                    quantity,
                    (
                        str(protection_plan.get("market_data_timestamp"))
                        if protection_plan and protection_plan.get("market_data_timestamp")
                        else None
                    ),
                ),
            )

            conn.execute(
                """
                INSERT INTO trades(
                    trade_id,owner_id,campaign_id,bot_id,strategy_id,
                    strategy_version,instrument,asset_class,exposure_class,
                    direction,quantity,entry_price,stop,structural_invalidation,
                    profit_plan,maximum_loss,opened_at,status,
                    protection_plan_id,protection_plan_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    trade_id, owner_id, campaign_id, bot_db, strategy_db,
                    strategy_version, instrument, asset_class, asset_class,
                    "LONG" if direction == 1 else "SHORT", quantity, price,
                    stop, structural_invalidation, profit_plan, maximum_loss,
                    now, "OPEN", protection_plan_id,
                    json.dumps(protection_plan, sort_keys=True) if protection_plan else None,
                ),
            )

            if direction == 1:

                cash_change = (
                    -order_notional
                )

            else:

                # Short positions are locally simulated.
                # We do not credit short-sale proceeds as
                # additional buying power.
                cash_change = 0.0

        else:

            old_side = int(
                current["side"]
            )

            old_qty = float(
                current["quantity"]
            )

            old_entry = float(
                current["average_price"]
            )

            if old_side == direction:

                new_qty = (
                    old_qty
                    + quantity
                )

                new_average = (
                    (
                        old_qty
                        * old_entry
                    )
                    + (
                        quantity
                        * price
                    )
                ) / new_qty

                conn.execute(
                    """
                    UPDATE positions

                    SET
                        quantity=?,
                        average_price=?,
                        last_price=?,
                        updated_at=?

                    WHERE position_id=?
                    """,
                    (
                        new_qty,
                        new_average,
                        price,
                        now,
                        current[
                            "position_id"
                        ],
                    ),
                )

                if direction == 1:

                    cash_change = (
                        -order_notional
                    )

            else:

                close_qty = min(
                    old_qty,
                    quantity,
                )

                pnl = (
                    close_qty
                    * (
                        price
                        - old_entry
                    )
                    * old_side
                )

                realized_delta += pnl

                remainder = (
                    old_qty
                    - close_qty
                )

                incoming_remainder = (
                    quantity
                    - close_qty
                )

                if incoming_remainder > 1e-12:
                    raise ValueError("A closing order cannot reverse an open position.")

                if old_side == 1:

                    cash_change += (
                        close_qty
                        * price
                    )
                else:
                    # Short-sale proceeds are not credited on entry, so realized
                    # short profit/loss is applied to cash when exposure closes.
                    cash_change += pnl

                if remainder > 1e-12:

                    conn.execute(
                        """
                        UPDATE positions

                        SET
                            quantity=?,
                            last_price=?,
                            realized_pnl=
                                realized_pnl + ?,
                            updated_at=?

                        WHERE position_id=?
                        """,
                        (
                            remainder,
                            price,
                            pnl,
                            now,
                            current[
                                "position_id"
                            ],
                        ),
                    )

                else:
                    conn.execute(
                        "DELETE FROM positions WHERE position_id=?",
                        (current["position_id"],),
                    )

                if current["trade_id"]:
                    trade_status = "OPEN" if remainder > 1e-12 else "CLOSED"
                    conn.execute(
                        """
                        UPDATE trades SET
                            exit_price=?, gross_pnl=COALESCE(gross_pnl,0)+?,
                            net_pnl=COALESCE(net_pnl,0)+?,
                            closed_at=CASE WHEN ?='CLOSED' THEN ? ELSE NULL END,
                            last_exit_at=?,
                            exit_reason=?, status=?
                        WHERE trade_id=?
                        """,
                        (
                            price, pnl, pnl, trade_status, now,
                            now, (metadata or {}).get("exit_reason", "PROTECTIVE_OR_MANUAL_EXIT"),
                            trade_status, current["trade_id"],
                        ),
                    )

        conn.execute(
            """
            UPDATE account

            SET
                cash=
                    cash + ?,

                realized_pnl=
                    realized_pnl + ?,

                updated_at=?

            WHERE id=1
            """,
            (
                cash_change,
                realized_delta,
                now,
            ),
        )

        conn.execute(
            """
            INSERT INTO orders(
                order_id,
                instrument,
                asset_class,
                side,
                quantity,
                price,
                notional,
                strategy_id,
                bot_id,
                signal_id,
                status,
                created_at,
                metadata_json
            )
            VALUES(
                ?,?,?,?,?,?,?,?,?,?,?,?,?
            )
            """,
            (
                order_id,
                instrument,
                asset_class,
                side,
                quantity,
                price,
                order_notional,
                strategy_db,
                bot_db,
                signal_id,
                "FILLED_LOCAL_PAPER",
                now,
                json.dumps(
                    metadata
                    or {}
                ),
            ),
        )

        conn.commit()

    record_training_event(
        instrument=instrument,
        strategy_id=strategy_id,
        bot_id=bot_id,
        event_type=(metadata or {}).get("training_event_type", "LOCAL_PAPER_FILL"),
        payload={
            "order_id":
                order_id,

            "side":
                side,

            "quantity":
                quantity,

            "price":
                price,

            "notional":
                order_notional,

            "signal_id":
                signal_id,
        },
    )

    # The canonical operations journal is append-only evidence. Notification
    # delivery consumes this record; Discord is never the ledger.
    from services.operations.store import record_event
    record_event(
        event_type=(metadata or {}).get(
            "operations_event_type",
            "paper.position_closed" if reducing else "paper.order_filled",
        ),
        source="local_paper_broker",
        subject_type="order",
        subject_id=order_id,
        state="CLOSED" if reducing else "OPEN",
        payload={
            "order_id": order_id, "instrument": instrument,
            "asset_class": asset_class, "side": side,
            "quantity": quantity, "price": price, "notional": order_notional,
            "strategy_id": strategy_id, "bot_id": bot_id,
            "signal_id": signal_id, "mode": "LOCAL_PAPER",
            "exit_reason": (metadata or {}).get("exit_reason"),
            "protection_plan_id": protection_plan_id,
        },
        evidence_ids=[value for value in (signal_id,) if value],
        versions={"strategy": strategy_version, "broker": "local-paper-v1"},
        dedup_key=f"paper-order:{order_id}",
    )

    return PaperOrder(
        order_id=order_id,
        instrument=instrument,
        asset_class=asset_class,
        side=side,
        quantity=quantity,
        price=price,
        notional=order_notional,
        strategy_id=strategy_id,
        bot_id=bot_id,
        signal_id=signal_id,
        status="FILLED_LOCAL_PAPER",
        created_at=now,
    )


def mark_price(
    instrument: str,
    price: float,
) -> None:

    if price <= 0:

        return

    with _connect() as conn:

        conn.execute(
            """
            UPDATE positions

            SET
                last_price=?,
                updated_at=?

            WHERE instrument=?
            """,
            (
                price,
                time.time(),
                instrument,
            ),
        )


def apply_protection_bar(
    instrument: str,
    bar: dict[str, Any],
    *,
    source: str = "London Strategic Edge OHLCV",
) -> list[dict[str, Any]]:
    """Evaluate one verified OHLC bar against local-paper protection plans.

    Same-bar stop/target ambiguity is resolved conservatively in favor of the
    stop. Trailing stops ratchet after the bar and therefore apply from the next
    source bar, avoiding within-bar path invention.
    """
    timestamp = str(bar.get("timestamp") or bar.get("time") or "")
    opened, high, low, closed = (float(bar[key]) for key in ("open", "high", "low", "close"))
    prices = (opened, high, low, closed)
    if (
        not timestamp
        or not all(math.isfinite(value) and value > 0 for value in prices)
        or high < max(opened, closed, low)
        or low > min(opened, closed, high)
    ):
        raise ValueError("A valid timestamped OHLC bar is required for protection evaluation.")
    events: list[dict[str, Any]] = []
    candidates = [row for row in positions() if row["instrument"] == instrument]

    def touched(level: float, direction: int, kind: str) -> bool:
        if kind == "stop":
            return low <= level if direction == 1 else high >= level
        return high >= level if direction == 1 else low <= level

    def exit_order(position: dict[str, Any], quantity: float, price: float, reason: str) -> None:
        side = "SELL" if int(position["side"]) == 1 else "BUY"
        order = submit_market_order(
            instrument=position["instrument"], asset_class=position["asset_class"],
            side=side, price=price, quantity=quantity,
            strategy_id=position.get("strategy_id"), bot_id=position.get("bot_id"),
            strategy_version=position.get("strategy_version") or "1",
            signal_id=f"auto:{position['position_id']}:{reason}", reduce_only=True,
            metadata={
                "exit_reason": reason, "source": source, "source_bar": timestamp,
                "training_event_type": reason,
                "operations_event_type": f"paper.{reason.lower()}",
            },
        )
        events.append({
            "position_id": position["position_id"], "order_id": order.order_id,
            "reason": reason, "quantity": quantity, "price": price,
            "source_bar": timestamp,
        })

    for position in candidates:
        if position.get("last_evaluated_bar") == timestamp:
            continue
        direction = int(position["side"])
        stop = float(position["stop"])
        plan = json.loads(position["protection_plan_json"]) if position.get("protection_plan_json") else {}
        state = json.loads(position["plan_state_json"]) if position.get("plan_state_json") else {
            "status": "LEGACY_STOP_ONLY", "target_1_filled": False, "trail_active": False,
        }
        # Records created before structured protection remain visible and
        # reviewable, but stale text/levels never gain execution authority.
        if int(position.get("legacy") or 0):
            state["status"] = "AWAITING_REVIEW"
            with _connect() as conn:
                conn.execute(
                    "UPDATE positions SET last_price=?,plan_state_json=?,last_evaluated_bar=?,updated_at=? WHERE position_id=?",
                    (closed, json.dumps(state, sort_keys=True), timestamp, time.time(), position["position_id"]),
                )
            continue
        # A newly entered user-defined plan has no source-bar identity. The
        # first observed bar establishes a baseline so pre-entry movement in an
        # already-open bar cannot manufacture an exit.
        if not plan and not position.get("last_evaluated_bar"):
            state["status"] = "ARMED_NEXT_BAR"
            with _connect() as conn:
                conn.execute(
                    "UPDATE positions SET last_price=?,plan_state_json=?,last_evaluated_bar=?,updated_at=? WHERE position_id=?",
                    (closed, json.dumps(state, sort_keys=True), timestamp, time.time(), position["position_id"]),
                )
            continue
        entry = float(position["average_price"])
        structural_stop = float(position.get("structural_invalidation") or 0.0)
        if (
            stop <= 0
            or structural_stop <= 0
            or (direction == 1 and structural_stop >= entry)
            or (direction == -1 and structural_stop <= entry)
        ):
            state["status"] = "INVALID_PROTECTION"
            with _connect() as conn:
                conn.execute(
                    "UPDATE positions SET last_price=?,plan_state_json=?,last_evaluated_bar=?,updated_at=? WHERE position_id=?",
                    (closed, json.dumps(state, sort_keys=True), timestamp, time.time(), position["position_id"]),
                )
            continue
        plan_type = plan.get("type", "USER_DEFINED")
        targets = plan.get("targets") or []
        active_target = None
        if plan_type == "FIXED_1_5R" and targets:
            active_target = float(targets[0]["price"])
        elif plan_type == "SCALE_1R_2R" and targets:
            active_target = float(targets[1 if state.get("target_1_filled") else 0]["price"])
        elif plan_type == "TRAIL_AFTER_1R" and targets and not state.get("trail_active"):
            active_target = float(targets[0]["price"])

        stop_hit = touched(stop, direction, "stop")
        target_hit = active_target is not None and touched(active_target, direction, "target")
        if stop_hit:
            base_fill = min(opened, stop) if direction == 1 else max(opened, stop)
            slippage = float(plan.get("cost_bps", os.getenv("FX_PAPER_MODELED_COST_BPS", "10"))) / 10_000
            fill = base_fill * (1 - slippage if direction == 1 else 1 + slippage)
            exit_order(position, float(position["quantity"]), fill, "AUTO_TRAIL" if state.get("trail_active") else "AUTO_STOP")
            continue

        if target_hit and plan_type == "FIXED_1_5R":
            exit_order(position, float(position["quantity"]), float(active_target), "AUTO_TARGET_1")
            continue

        if target_hit and plan_type == "SCALE_1R_2R":
            if not state.get("target_1_filled"):
                first_quantity = min(float(position["quantity"]), float(position.get("initial_quantity") or position["quantity"]) * 0.5)
                exit_order(position, first_quantity, float(active_target), "AUTO_TARGET_1")
                cost_bps = float(plan.get("cost_bps", 0.0))
                breakeven = float(position["average_price"]) * (1 + direction * cost_bps / 10_000)
                state.update({"target_1_filled": True, "status": "TARGET_1_FILLED", "effective_stop": breakeven})
                with _connect() as conn:
                    conn.execute(
                        "UPDATE positions SET stop=?,plan_state_json=?,last_evaluated_bar=?,updated_at=? WHERE position_id=?",
                        (breakeven, json.dumps(state, sort_keys=True), timestamp, time.time(), position["position_id"]),
                    )
                if len(targets) > 1 and touched(float(targets[1]["price"]), direction, "target"):
                    remaining = next((row for row in positions() if row["position_id"] == position["position_id"]), None)
                    if remaining:
                        exit_order(remaining, float(remaining["quantity"]), float(targets[1]["price"]), "AUTO_TARGET_2")
                continue
            exit_order(position, float(position["quantity"]), float(active_target), "AUTO_TARGET_2")
            continue

        if target_hit and plan_type == "TRAIL_AFTER_1R":
            cost_bps = float(plan.get("cost_bps", 0.0))
            breakeven = float(position["average_price"]) * (1 + direction * cost_bps / 10_000)
            state.update({"trail_active": True, "status": "TRAIL_ACTIVE", "effective_stop": breakeven})
            stop = breakeven

        if state.get("trail_active"):
            atr = float(plan.get("atr_14") or 0.0)
            candidate_stop = high - atr if direction == 1 else low + atr
            stop = max(stop, candidate_stop) if direction == 1 else min(stop, candidate_stop)
            state["effective_stop"] = stop

        with _connect() as conn:
            conn.execute(
                "UPDATE positions SET stop=?,last_price=?,plan_state_json=?,last_evaluated_bar=?,updated_at=? WHERE position_id=?",
                (stop, closed, json.dumps(state, sort_keys=True), timestamp, time.time(), position["position_id"]),
            )
    return events


def close_position(
    position_id: str,
    price: float,
) -> dict:

    with _connect() as conn:

        position = conn.execute(
            """
            SELECT *
            FROM positions

            WHERE position_id=?
            """,
            (
                position_id,
            ),
        ).fetchone()

    if not position:

        raise ValueError(
            "Position not found."
        )

    item = dict(
        position
    )

    opposite = (
        "SELL"
        if int(
            item["side"]
        ) == 1
        else "BUY"
    )

    order = submit_market_order(
        instrument=item[
            "instrument"
        ],

        asset_class=item[
            "asset_class"
        ],

        side=opposite,

        price=price,

        quantity=float(
            item[
                "quantity"
            ]
        ),

        strategy_id=(
            item.get(
                "strategy_id"
            )
            or None
        ),

        bot_id=(
            item.get(
                "bot_id"
            )
            or None
        ),

        metadata={
            "close_position":
                position_id
        },
        reduce_only=True,
    )

    return asdict(
        order
    )


def reset_account(
    starting_cash: float | None = None,
) -> None:

    cash = float(
        starting_cash
        or _starting_cash()
    )

    now = time.time()

    with _connect() as conn:

        conn.execute(
            "DELETE FROM positions"
        )

        conn.execute(
            "DELETE FROM orders"
        )

        conn.execute(
            "DELETE FROM equity_history"
        )

        conn.execute(
            """
            UPDATE account

            SET
                starting_cash=?,
                cash=?,
                realized_pnl=0,
                updated_at=?

            WHERE id=1
            """,
            (
                cash,
                cash,
                now,
            ),
        )

        conn.commit()
