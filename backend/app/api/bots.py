from fastapi import APIRouter

from backend.app.services.bots.registry import (
    BOTS,
)


router = APIRouter(
    prefix="/api/bots",
    tags=["Bots"],
)


@router.get("")
async def bots():

    return {
        "ok": True,
        "bots": BOTS,
    }
