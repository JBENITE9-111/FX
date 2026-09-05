from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import asdict, dataclass

import keyring

from services.auth.totp import totp_service

SERVICE_NAME = "FX_TRADING_OS_APPROVAL"
SIGNING_KEY_NAME = "live-approval-signing-key"

@dataclass(frozen=True)
class ApprovalPayload:
    proposal_id: str
    instrument: str
    side: str
    quantity: float
    order_type: str
    max_notional: float
    risk_decision_id: str
    expires_at: int
    nonce: str

def _signing_key() -> bytes:
    key = keyring.get_password(SERVICE_NAME, SIGNING_KEY_NAME)
    if not key:
        key = secrets.token_hex(32)
        keyring.set_password(SERVICE_NAME, SIGNING_KEY_NAME, key)
    return bytes.fromhex(key)

def issue_live_approval(payload: ApprovalPayload, totp_code: str) -> str:
    if not totp_service.verify(totp_code, valid_window=1, allow_recovery=False):
        raise PermissionError("Invalid TOTP code.")

    now = int(time.time())
    ttl = int(os.getenv("FX_LIVE_APPROVAL_TTL_SECONDS", "90"))

    if payload.expires_at <= now or payload.expires_at > now + ttl:
        raise PermissionError("Approval expiry is invalid.")

    body = json.dumps(
        asdict(payload),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()

    signature = hmac.new(
        _signing_key(),
        body,
        hashlib.sha256,
    ).hexdigest()

    return f"{body.hex()}.{signature}"

def verify_live_approval(token: str, expected: ApprovalPayload) -> bool:
    try:
        body_hex, supplied = token.split(".", 1)
        body = bytes.fromhex(body_hex)

        expected_sig = hmac.new(
            _signing_key(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(supplied, expected_sig):
            return False

        decoded = json.loads(body)
        if decoded != asdict(expected):
            return False

        return int(decoded["expires_at"]) > int(time.time())
    except Exception:
        return False
