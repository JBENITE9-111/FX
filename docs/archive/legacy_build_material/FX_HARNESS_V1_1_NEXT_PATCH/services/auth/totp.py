from __future__ import annotations

import io
import os
from dataclasses import dataclass

import keyring
import pyotp
import qrcode


SERVICE_NAME = "FX_TRADING_OS_TOTP"


@dataclass(frozen=True)
class TotpConfig:
    account: str = os.getenv("FX_AUTH_ACCOUNT", "jacobo")
    issuer: str = os.getenv("FX_AUTH_ISSUER", "FX")


class TotpService:
    """RFC 6238 TOTP service compatible with Google Authenticator.

    The secret is stored in the OS keychain via keyring.
    It is never written to .env or returned by normal status endpoints.
    """

    def __init__(self, config: TotpConfig | None = None):
        self.config = config or TotpConfig()

    @property
    def _key_name(self) -> str:
        return f"{self.config.issuer}:{self.config.account}"

    def is_enrolled(self) -> bool:
        return bool(keyring.get_password(SERVICE_NAME, self._key_name))

    def enroll(self, *, rotate: bool = False) -> dict[str, str | bytes]:
        existing = keyring.get_password(SERVICE_NAME, self._key_name)
        if existing and not rotate:
            raise RuntimeError("TOTP is already enrolled. Use rotate=True to replace it.")

        secret = pyotp.random_base32()
        keyring.set_password(SERVICE_NAME, self._key_name, secret)

        uri = pyotp.TOTP(secret).provisioning_uri(
            name=self.config.account,
            issuer_name=self.config.issuer,
        )

        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        # Return secret only during explicit enrollment. UI must show once.
        return {
            "secret": secret,
            "provisioning_uri": uri,
            "qr_png": buf.getvalue(),
        }

    def verify(self, code: str, *, valid_window: int = 1) -> bool:
        secret = keyring.get_password(SERVICE_NAME, self._key_name)
        if not secret:
            return False
        value = "".join(ch for ch in str(code) if ch.isdigit())
        if len(value) != 6:
            return False
        return bool(pyotp.TOTP(secret).verify(value, valid_window=valid_window))

    def remove(self) -> None:
        try:
            keyring.delete_password(SERVICE_NAME, self._key_name)
        except keyring.errors.PasswordDeleteError:
            pass


totp_service = TotpService()
