from fastapi import APIRouter, HTTPException

from backend.app.services.brokers.alpaca_paper import (
    AlpacaPaperBroker,
)


router = APIRouter(
    prefix="/api/broker",
    tags=["broker"],
)


@router.get("/paper/account")
async def paper_account():
    try:
        broker = AlpacaPaperBroker()

        account = broker.account()

        return {
            "id": str(account.id),
            "status": str(account.status),
            "currency": account.currency,
            "cash": str(account.cash),
            "equity": str(account.equity),
            "buying_power": str(
                account.buying_power
            ),
            "paper": True,
            "live": False,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/paper/positions")
async def paper_positions():
    try:
        broker = AlpacaPaperBroker()

        positions = broker.positions()

        return {
            "paper": True,
            "positions": [
                {
                    "symbol": p.symbol,
                    "qty": str(p.qty),
                    "side": str(p.side),
                    "market_value": str(
                        p.market_value
                    ),
                    "avg_entry_price": str(
                        p.avg_entry_price
                    ),
                    "unrealized_pl": str(
                        p.unrealized_pl
                    ),
                }
                for p in positions
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
