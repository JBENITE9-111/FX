from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

import keyring

SERVICE_NAME = "FX_TRADING_OS_SESSION"
SIGNING_KEY_NAME = "browser-session-signing-key"
COOKIE_NAME = "fx_secure_session"


def _key() -> bytes:
    value = keyring.get_password(SERVICE_NAME, SIGNING_KEY_NAME)
    if not value:
        value = secrets.token_hex(32)
        keyring.set_password(SERVICE_NAME, SIGNING_KEY_NAME, value)
    return bytes.fromhex(value)


def issue_session(ttl_seconds: int = 8 * 60 * 60) -> str:
    payload = json.dumps(
        {"exp": int(time.time()) + ttl_seconds, "nonce": secrets.token_hex(16)},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(_key(), encoded, hashlib.sha256).digest()
    return f"{encoded.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def verify_session(token: str | None) -> bool:
    try:
        encoded, supplied = (token or "").split(".", 1)
        expected = base64.urlsafe_b64encode(
            hmac.new(_key(), encoded.encode(), hashlib.sha256).digest()
        ).rstrip(b"=").decode()
        if not hmac.compare_digest(supplied, expected):
            return False
        padding = "=" * (-len(encoded) % 4)
        payload = json.loads(base64.urlsafe_b64decode(encoded + padding))
        return int(payload["exp"]) > int(time.time())
    except Exception:
        return False
