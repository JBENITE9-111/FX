from __future__ import annotations

import hashlib
import io
import json
import os
import secrets
import sqlite3
import threading
import time
from dataclasses import dataclass

import keyring
import pyotp
import qrcode
from pathlib import Path

SERVICE_NAME = "FX_TRADING_OS_TOTP"
THROTTLE_DB = Path("/Users/macmac/Documents/Codex/FX/data/auth/totp_throttle.sqlite3")


@dataclass(frozen=True)
class TotpConfig:
    account: str = os.getenv("FX_AUTH_ACCOUNT", "jacobo")
    issuer: str = os.getenv("FX_AUTH_ISSUER", "FX")


class TotpService:
    def __init__(self, config: TotpConfig | None = None):
        self.config = config or TotpConfig()
        self._lock = threading.Lock()
        THROTTLE_DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(THROTTLE_DB) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS totp_throttle(
                identity TEXT PRIMARY KEY, failures INTEGER NOT NULL DEFAULT 0,
                locked_until REAL NOT NULL DEFAULT 0, updated_at REAL NOT NULL)""")

    def _throttle(self) -> tuple[int, float]:
        with sqlite3.connect(THROTTLE_DB) as conn:
            row = conn.execute("SELECT failures,locked_until FROM totp_throttle WHERE identity=?", (self._key_name,)).fetchone()
        return (int(row[0]), float(row[1])) if row else (0, 0.0)

    def _write_throttle(self, failures: int, locked_until: float) -> None:
        with sqlite3.connect(THROTTLE_DB) as conn:
            conn.execute("""INSERT INTO totp_throttle(identity,failures,locked_until,updated_at) VALUES(?,?,?,?)
                ON CONFLICT(identity) DO UPDATE SET failures=excluded.failures,
                locked_until=excluded.locked_until,updated_at=excluded.updated_at""",
                (self._key_name, failures, locked_until, time.time()))

    @property
    def _key_name(self) -> str:
        return f"{self.config.issuer}:{self.config.account}"

    @property
    def _pending_key_name(self) -> str:
        return f"{self._key_name}:pending"

    @property
    def _recovery_key_name(self) -> str:
        return f"{self._key_name}:recovery"

    def is_enrolled(self) -> bool:
        return bool(keyring.get_password(SERVICE_NAME, self._key_name))

    def enroll(self, *, rotate: bool = False, current_code: str = "") -> dict:
        if self.is_enrolled() and not rotate:
            raise RuntimeError("TOTP is already enrolled.")
        if self.is_enrolled() and rotate and not self.verify(current_code):
            raise PermissionError("The current TOTP code is required to rotate 2FA.")

        secret = pyotp.random_base32()
        keyring.set_password(SERVICE_NAME, self._pending_key_name, secret)
        uri = pyotp.TOTP(secret).provisioning_uri(
            name=self.config.account,
            issuer_name=self.config.issuer,
        )
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return {"secret": secret, "provisioning_uri": uri, "qr_png": buffer.getvalue()}

    @staticmethod
    def _digits(code: str) -> str:
        return "".join(ch for ch in str(code) if ch.isdigit())

    def _record_failure(self) -> None:
        with self._lock:
            failures, _ = self._throttle()
            failures += 1
            if failures >= 5:
                self._write_throttle(0, time.time() + 60)
            else:
                self._write_throttle(failures, 0.0)

    def _clear_failures(self) -> None:
        with self._lock:
            self._write_throttle(0, 0.0)

    def retry_after(self) -> int:
        _, locked_until = self._throttle()
        return max(0, int(locked_until - time.time()))

    def confirm_enrollment(self, code: str) -> dict:
        secret = keyring.get_password(SERVICE_NAME, self._pending_key_name)
        value = self._digits(code)
        if not secret or len(value) != 6 or not pyotp.TOTP(secret).verify(value, valid_window=1):
            self._record_failure()
            raise PermissionError("The setup code is invalid or expired.")
        recovery_codes = [f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}" for _ in range(8)]
        hashes = [hashlib.sha256(item.encode()).hexdigest() for item in recovery_codes]
        keyring.set_password(SERVICE_NAME, self._key_name, secret)
        keyring.set_password(SERVICE_NAME, self._recovery_key_name, json.dumps(hashes))
        try:
            keyring.delete_password(SERVICE_NAME, self._pending_key_name)
        except keyring.errors.PasswordDeleteError:
            pass
        self._clear_failures()
        return {"recovery_codes": recovery_codes}

    def verify(self, code: str, *, valid_window: int = 1, allow_recovery: bool = False) -> bool:
        if self.retry_after() > 0:
            return False
        secret = keyring.get_password(SERVICE_NAME, self._key_name)
        if not secret:
            return False
        value = self._digits(code)
        if len(value) == 6 and pyotp.TOTP(secret).verify(value, valid_window=valid_window):
            self._clear_failures()
            return True
        if allow_recovery:
            supplied_hash = hashlib.sha256(str(code).strip().upper().encode()).hexdigest()
            try:
                hashes = json.loads(keyring.get_password(SERVICE_NAME, self._recovery_key_name) or "[]")
            except json.JSONDecodeError:
                hashes = []
            if supplied_hash in hashes:
                hashes.remove(supplied_hash)
                keyring.set_password(SERVICE_NAME, self._recovery_key_name, json.dumps(hashes))
                self._clear_failures()
                return True
        self._record_failure()
        return False


totp_service = TotpService()
