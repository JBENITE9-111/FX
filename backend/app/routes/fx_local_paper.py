from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
import asyncio
import json

from pydantic import (
    BaseModel,
    Field,
)

from services.local_paper.broker import (
    close_position,
    get_account,
    get_order_by_signal,
    mark_price,
    create_protection_plan,
    consume_protection_plan,
    local_risk_capacity,
    validate_protection_plan,
    positions,
    reset_account,
    submit_market_order,
)
from services.local_paper.protection import build_plan_options
from services.local_paper.monitor import refresh_open_position_marks
from backend.app.services.market_data.lse_global import LSEGlobalMarketData
from services.learning.status import learning_overview


RESEARCH_SETUP_BY_ASSET = {
    "Stocks": ("trend_following", "Trend Following"),
    "ETFs": ("regime_trend", "Regime-Aware Trend"),
    "Indices": ("regime_trend", "Regime-Aware Trend"),
    "Forex": ("macd_trend", "MACD Trend"),
    "Commodities": ("kalman_trend", "Kalman Trend"),
    "Crypto": ("momentum", "Momentum"),
    "Futures": ("breakout", "20-Period Breakout"),
}


router = APIRouter(
    prefix="/api/local-paper",
    tags=["Local Paper"],
)


class PaperOrderRequest(
    BaseModel,
):

    instrument: str

    asset_class: str = "unknown"

    side: str

    price: float = Field(
        gt=0
    )

    quantity: float | None = Field(
        default=None,
        gt=0,
    )

    notional: float | None = Field(
        default=None,
        gt=0,
    )

    strategy_id: str | None = None

    bot_id: str | None = None

    signal_id: str | None = None

    stop: float | None = Field(default=None, gt=0)
    structural_invalidation: float | None = Field(default=None, gt=0)
    profit_plan: str | None = None
    maximum_loss: float | None = Field(default=None, gt=0)
    campaign_id: str | None = None
    strategy_version: str = "1"
    protection_plan_id: str | None = None
    plan_source: str = Field(default="USER_DEFINED", pattern="^(USER_DEFINED|FX_SUGGESTED)$")


class CloseRequest(
    BaseModel,
):

    price: float = Field(
        gt=0
    )


class MarkRequest(
    BaseModel,
):

    instrument: str

    price: float = Field(
        gt=0
    )


@router.get(
    "/account"
)
def account():

    return get_account()


@router.get(
    "/positions"
)
def paper_positions():

    return {
        "positions":
            positions()
    }


@router.get("/strategy-suggestion/{instrument:path}")
def strategy_suggestion(instrument: str, asset_class: str = "Stocks"):
    """Describe real qualification evidence for one instrument.

    The fallback setup is a research template, never an approval. This keeps the
    order form useful while preserving the promotion pipeline's actual state.
    """
    symbol = instrument.strip().upper()
    records = [
        item for item in learning_overview()["records"]
        if item.get("is_current") and str(item.get("instrument") or "").upper() == symbol
    ]
    approved = [item for item in records if item.get("eligible")]

    def evidence_score(item: dict) -> tuple[int, float]:
        values = [
            item.get("unseen_auc"), item.get("unseen_balanced_accuracy"),
            item.get("walk_forward_auc"), item.get("walk_forward_balanced_accuracy"),
        ]
        minimum = min((float(value) for value in values if value is not None), default=0.0)
        return (1 if item.get("stage") == "EXAMINATION" else 0, minimum)

    best = max(records, key=evidence_score) if records else None
    strategy_id, strategy_name = RESEARCH_SETUP_BY_ASSET.get(
        asset_class, RESEARCH_SETUP_BY_ASSET["Stocks"]
    )
    approved_record = max(approved, key=evidence_score) if approved else None
    return {
        "ok": True,
        "instrument": symbol,
        "asset_class": asset_class,
        "status": "APPROVED" if approved_record else "NO_APPROVED_STRATEGY",
        "paper_action": "READY_FOR_PROTECTED_PAPER" if approved_record else "WAIT",
        "approved_strategy": ({
            "strategy_id": approved_record.get("strategy_id") or strategy_id,
            "model": approved_record.get("model"),
            "stage": approved_record.get("stage"),
        } if approved_record else None),
        "research_setup": {
            "strategy_id": strategy_id,
            "name": strategy_name,
            "status": "RESEARCH_ONLY",
            "reason": f"A suitable starting hypothesis for {asset_class.lower()} research; it has not been approved for {symbol}.",
        },
        "best_model_evidence": ({
            "model": best.get("model"),
            "stage": best.get("stage"),
            "blocked_at": best.get("blocked_at"),
            "unseen_auc": best.get("unseen_auc"),
            "walk_forward_auc": best.get("walk_forward_auc"),
            "explanation": best.get("explanation"),
        } if best else None),
        "message": (
            "A strategy version has passed the recorded promotion gates. Review its protected paper proposal."
            if approved_record else
            "No strategy is approved for this instrument yet. FX will keep WAIT as the executable decision while research continues."
        ),
    }


@router.post("/positions/refresh-marks")
async def refresh_position_marks():
    """Mark open paper positions from the research market-data feed."""
    try:
        return await asyncio.to_thread(refresh_open_position_marks)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The market-data provider is unavailable.") from exc


@router.get("/protection-suggestions")
async def protection_suggestions(
    instrument: str = Query(min_length=1),
    asset_class: str = "Stocks",
    direction: str = Query(pattern="^(BUY|SELL)$"),
    notional: float = Query(default=100.0, gt=0),
    strategy_id: str = Query(min_length=1),
    bot_id: str = Query(min_length=1),
):
    timeframe = {"Stocks": "1d", "ETFs": "1d", "Indices": "1d", "Futures": "1d", "Forex": "1h", "Crypto": "1h", "Commodities": "4h"}.get(asset_class, "1d")
    try:
        rows = await asyncio.to_thread(LSEGlobalMarketData().candles, instrument, timeframe, 80)
        if len(rows) < 20:
            raise ValueError("not enough history")
        highs = [float(row["high"]) for row in rows]
        lows = [float(row["low"]) for row in rows]
        closes = [float(row["close"]) for row in rows]
        true_ranges = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1])) for i in range(1, len(rows))]
        atr = sum(true_ranges[-14:]) / min(14, len(true_ranges))
        entry = closes[-1]
        if direction == "BUY":
            stop = min(min(lows[-20:]), entry - 1.5 * atr)
            risk = entry - stop
        else:
            stop = max(max(highs[-20:]), entry + 1.5 * atr)
            risk = stop - entry
        if risk <= 0:
            raise ValueError("invalid volatility estimate")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="FX could not calculate a protected plan from current market history.") from exc
    market_timestamp = str(rows[-1].get("timestamp") or rows[-1].get("time") or "UNKNOWN")
    if market_timestamp == "UNKNOWN":
        raise HTTPException(status_code=503, detail="Current market history has no verified timestamp.")
    capacity = local_risk_capacity()
    generated = build_plan_options(
        instrument=instrument, asset_class=asset_class, direction=direction,
        entry=entry, stop=stop, atr_14=atr, notional=notional,
        timeframe=timeframe,
        market_data_timestamp=market_timestamp,
        strategy_id=strategy_id, bot_id=bot_id, risk_capacity=capacity,
    )
    plans = [create_protection_plan(plan) for plan in generated["plans"]]
    return {
        "ok": True, "instrument": instrument, "direction": direction,
        "entry": entry, "structural_stop": stop, "atr_14": atr,
        "maximum_loss": generated["risk"]["planned_loss_envelope"],
        "risk": generated["risk"], "plans": plans,
        "warning": generated["warning"], "source": "London Strategic Edge OHLCV",
        "timeframe": timeframe, "research_only": True,
    }


@router.post(
    "/orders"
)
def order(
    request: PaperOrderRequest,
):

    try:

        existing = get_order_by_signal(request.signal_id)
        if existing:
            requested_side = request.side.strip().upper().replace("LONG", "BUY").replace("SHORT", "SELL")
            existing_side = existing.side.replace("LONG", "BUY").replace("SHORT", "SELL")
            same_request = (
                existing.instrument.upper() == request.instrument.upper()
                and existing.asset_class == request.asset_class
                and existing_side == requested_side
                and (existing.strategy_id or "") == (request.strategy_id or "")
                and (existing.bot_id or "") == (request.bot_id or "")
                and (request.notional is None or abs(existing.notional - request.notional) <= max(0.01, existing.notional * 0.001))
            )
            if not same_request:
                raise ValueError("The signal ID was already used by a different paper order.")
            return existing.__dict__

        structured_plan = None
        profit_plan = request.profit_plan
        stop = request.stop
        structural_invalidation = request.structural_invalidation
        maximum_loss = request.maximum_loss
        if request.plan_source == "FX_SUGGESTED" and not request.protection_plan_id:
            raise ValueError("Select a current FX protection plan or use a complete user-defined plan.")
        if request.protection_plan_id and request.plan_source != "FX_SUGGESTED":
            raise ValueError("The protection-plan source does not match the selected generated plan.")
        if request.protection_plan_id:
            structured_plan = validate_protection_plan(
                request.protection_plan_id,
                instrument=request.instrument, asset_class=request.asset_class,
                direction=request.side.upper(), entry=request.price,
                notional=float(request.notional or 0),
                strategy_id=str(request.strategy_id or ""), bot_id=str(request.bot_id or ""),
            )
            stop = float(structured_plan["structural_stop"])
            structural_invalidation = stop
            maximum_loss = float(structured_plan["maximum_loss"])
            profit_plan = json.dumps({
                "type": structured_plan["type"], "label": structured_plan["label"],
                "targets": structured_plan.get("targets", []),
                "management": structured_plan["management"],
            }, sort_keys=True)

        result = submit_market_order(
            instrument=
                request.instrument,

            asset_class=
                request.asset_class,

            side=
                request.side,

            price=
                request.price,

            quantity=
                request.quantity,

            notional=
                request.notional,

            strategy_id=
                request.strategy_id,

            bot_id=
                request.bot_id,

            signal_id=
                request.signal_id,

            stop=stop,
            structural_invalidation=structural_invalidation,
            profit_plan=profit_plan,
            maximum_loss=maximum_loss,
            campaign_id=request.campaign_id,
            strategy_version=request.strategy_version,
            protection_plan_id=request.protection_plan_id,
            protection_plan=structured_plan,
        )

        if request.protection_plan_id:
            consume_protection_plan(request.protection_plan_id)
        return result.__dict__

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post(
    "/positions/{position_id}/close"
)
def close(
    position_id: str,
    request: CloseRequest,
):

    try:

        return close_position(
            position_id,
            request.price,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post(
    "/mark"
)
def mark(
    request: MarkRequest,
):

    mark_price(
        request.instrument,
        request.price,
    )

    return {
        "status":
            "OK"
    }


@router.post(
    "/reset"
)
def reset():

    reset_account()

    return {
        "status":
            "RESET",

        "account":
            get_account(),
    }
