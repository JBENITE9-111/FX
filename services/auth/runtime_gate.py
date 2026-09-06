from __future__ import annotations

import asyncio
import os
import time
from typing import Any


def _enabled(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


class AutomationRuntimeGate:
    """Process-local TOTP gate for research and paper automation."""

    def __init__(self) -> None:
        self._unlocked = False
        self._unlocked_at: float | None = None
        self._unlocked_by: str | None = None
        self._lock = asyncio.Lock()

    def required(self) -> bool:
        return _enabled("FX_REQUIRE_TOTP_FOR_AUTOMATION", True)

    def status(self) -> dict[str, Any]:
        return {
            "required": self.required(),
            "unlocked": self._unlocked,
            "state": "UNLOCKED" if self._unlocked else "AWAITING_TOTP",
            "unlocked_at": self._unlocked_at,
            "unlocked_by": self._unlocked_by,
            "unlock_url": "/security",
        }

    async def unlock(self, source: str = "TOTP") -> dict[str, Any]:
        async with self._lock:
            if self._unlocked:
                return self.status()

            from backend.app.services.bots.runtime import bots
            from services.learning.continuous import continuous_learning
            from services.operations.scheduler import scheduler

            scheduler.start()
            if _enabled("FX_AUTO_LEARN_ON_STARTUP", True):
                continuous_learning.start(source)
            if _enabled("FX_AUTO_START_BOTS", True):
                for item in bots.list():
                    bots.start(item["id"])

            self._unlocked = True
            self._unlocked_at = time.time()
            self._unlocked_by = source
            return self.status()


automation_runtime_gate = AutomationRuntimeGate()
