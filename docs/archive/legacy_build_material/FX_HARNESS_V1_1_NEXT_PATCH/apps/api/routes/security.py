from __future__ import annotations

import base64
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.auth.approval import ApprovalPayload, issue_live_approval
from services.auth.totp import totp_service


router = APIRouter(prefix="/security", tags=["security"])


class EnrollRequest(BaseModel):
    rotate: bool = False


class LiveApprovalRequest(BaseModel):
    proposal_id: str
    instrument: str
    side: str
    quantity: float = Field(gt=0)
    order_type: str
    max_notional: float = Field(gt=0)
    risk_decision_id: str
    totp_code: str = Field(min_length=6, max_length=8)


@router.get("/totp/status")
def totp_status():
    return {"enrolled": totp_service.is_enrolled()}


@router.post("/totp/enroll")
def totp_enroll(req: EnrollRequest):
    try:
        result = totp_service.enroll(rotate=req.rotate)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {
        "secret": result["secret"],
        "provisioning_uri": result["provisioning_uri"],
        "qr_png_base64": base64.b64encode(result["qr_png"]).decode(),
        "warning": "Display once. Do not log or persist the secret in the browser.",
    }


@router.post("/live-approval")
def live_approval(req: LiveApprovalRequest):
    ttl = 90
    payload = ApprovalPayload(
        proposal_id=req.proposal_id,
        instrument=req.instrument,
        side=req.side,
        quantity=req.quantity,
        order_type=req.order_type,
        max_notional=req.max_notional,
        risk_decision_id=req.risk_decision_id,
        expires_at=int(time.time()) + ttl,
        nonce=__import__("secrets").token_hex(16),
    )
    try:
        token = issue_live_approval(payload, req.totp_code)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return {"approval_token": token, "expires_at": payload.expires_at, "payload": payload.__dict__}
