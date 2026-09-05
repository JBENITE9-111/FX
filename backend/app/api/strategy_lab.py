from fastapi import (
    APIRouter,
)

from backend.app.services.market_data.lse_global import (
    LSEGlobalMarketData,
)

from backend.app.services.models.historical_analogues import (
    find_analogues,
)

from backend.app.services.models.macro import (
    MacroContextEngine,
)

from backend.app.services.models.council import (
    model_council,
)

from backend.app.services.strategies.backtester import (
    backtest,
)

from backend.app.services.strategies.proposals import (
    approve_paper_proposal,
    create_paper_proposal,
)


router = APIRouter(
    prefix="/api/strategy-lab",
    tags=["Strategy Lab"],
)


@router.get(
    "/{strategy_id}/{symbol:path}"
)
async def analyse(
    strategy_id: str,
    symbol: str,
    timeframe: str = "1d",
):

    try:

        data = (
            LSEGlobalMarketData()
        )

        rows = data.candles(
            symbol=symbol,
            timeframe=timeframe,
            limit=500,
        )

        backtest_result = backtest(
            strategy_id,
            rows,
        )

        council = model_council(
            rows
        )

        analogues = find_analogues(
            rows
        )

        macro = (
            MacroContextEngine()
            .snapshot(
                timeframe="1d"
            )
        )

        latest = rows[-1]

        return {
            "ok": True,
            "symbol": symbol,
            "strategy": strategy_id,
            "timeframe": timeframe,
            "source": (
                "London Strategic Edge"
            ),
            "latest_price": (
                latest.get(
                    "close"
                )
                or latest.get(
                    "c"
                )
            ),
            "backtest": (
                backtest_result
            ),
            "model_council": (
                council
            ),
            "historical_analogues": (
                analogues
            ),
            "macro": macro,
            "mode": "RESEARCH / PAPER",
            "real_money": False,
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }


@router.post(
    "/{strategy_id}/{symbol}/propose-paper"
)
async def propose(
    strategy_id: str,
    symbol: str,
):

    try:

        service = (
            LSEGlobalMarketData()
        )

        rows = service.candles(
            symbol=symbol,
            timeframe="1d",
            limit=500,
        )

        proposal = (
            create_paper_proposal(
                strategy_id,
                symbol,
                rows,
            )
        )

        return {
            "ok": True,
            "proposal": proposal,
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }


@router.post(
    "/proposals/{proposal_id}/approve"
)
async def approve(
    proposal_id: str,
):

    try:

        proposal = (
            approve_paper_proposal(
                proposal_id
            )
        )

        return {
            "ok": True,
            "proposal": proposal,
            "message": (
                "The approved Paper trade was submitted to Alpaca Paper."
            ),
        }

    except Exception as exc:

        return {
            "ok": False,
            "message": str(exc),
        }
