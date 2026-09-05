from __future__ import annotations

from fastapi import (
    APIRouter,
    HTTPException,
)

from services.bot_signals.store import (
    get_signal,
    list_signals,
)


router = APIRouter(
    prefix="/api/bot-signals",
    tags=["Bot Signals"],
)


@router.get("")
def signals(
    limit: int = 100,
):

    return {
        "signals":
            list_signals(
                limit=min(
                    max(
                        1,
                        limit,
                    ),
                    500,
                )
            )
    }


@router.get(
    "/{signal_id}"
)
def signal(
    signal_id: str,
):

    result = get_signal(
        signal_id
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Signal not found."
            ),
        )

    return result
