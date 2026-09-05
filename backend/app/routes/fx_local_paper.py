from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)
import asyncio
from datetime import datetime, timezone

from pydantic import (
    BaseModel,
    Field,
)

from services.local_paper.broker import (
    close_position,
    get_account,
    mark_price,
    positions,
    reset_account,
    submit_market_order,
)
from backend.app.services.market_data.lse_global import LSEGlobalMarketData


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


@router.post("/positions/refresh-marks")
async def refresh_position_marks():
    """Mark open paper positions from the research market-data feed."""
    open_positions = positions()
    instruments = {}
    timeframes = {"Stocks": "1d", "ETFs": "1d", "Indices": "1d", "Futures": "1d", "Forex": "1h", "Crypto": "1h", "Commodities": "4h"}
    for position in open_positions:
        instruments[position["instrument"]] = timeframes.get(position.get("asset_class"), "1d")
    updated, failures = [], []
    try:
        service = LSEGlobalMarketData()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The market-data provider is unavailable.") from exc
    for instrument, timeframe in instruments.items():
        try:
            rows = await asyncio.to_thread(service.candles, instrument, timeframe, 2)
            price = float(rows[-1]["close"])
            mark_price(instrument, price)
            updated.append({"instrument": instrument, "price": price, "timeframe": timeframe})
        except Exception:
            failures.append(instrument)
    return {"ok": bool(updated) or not instruments, "source": "London Strategic Edge", "marked_at": datetime.now(timezone.utc).isoformat(), "updated": updated, "failed": failures}


@router.get("/protection-suggestions")
async def protection_suggestions(
    instrument: str = Query(min_length=1),
    asset_class: str = "Stocks",
    direction: str = Query(pattern="^(BUY|SELL)$"),
    notional: float = Query(default=100.0, gt=0),
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
            targets = [entry + risk, entry + 1.5 * risk, entry + 2 * risk]
        else:
            stop = max(max(highs[-20:]), entry + 1.5 * atr)
            risk = stop - entry
            targets = [entry - risk, entry - 1.5 * risk, entry - 2 * risk]
        if risk <= 0:
            raise ValueError("invalid volatility estimate")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="FX could not calculate a protected plan from current market history.") from exc
    plans = [
        {"id": "FIXED_1_5R", "label": "Fixed target at 1.5R", "description": f"Exit the full paper position near {targets[1]:.6g}."},
        {"id": "SCALE_1R_2R", "label": "Scale at 1R and 2R", "description": f"Take half near {targets[0]:.6g} and the rest near {targets[2]:.6g}."},
        {"id": "TRAIL_AFTER_1R", "label": "Trail after 1R", "description": f"At {targets[0]:.6g}, move the stop by a validated 1 ATR trail ({atr:.6g})."},
    ]
    return {"ok": True, "instrument": instrument, "direction": direction, "entry": entry, "structural_stop": stop, "atr_14": atr, "maximum_loss": round(min(10.0, max(1.0, notional * 0.01)), 2), "plans": plans, "source": "London Strategic Edge OHLCV", "timeframe": timeframe, "research_only": True}


@router.post(
    "/orders"
)
def order(
    request: PaperOrderRequest,
):

    try:

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

            stop=request.stop,
            structural_invalidation=request.structural_invalidation,
            profit_plan=request.profit_plan,
            maximum_loss=request.maximum_loss,
            campaign_id=request.campaign_id,
            strategy_version=request.strategy_version,
        )

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
