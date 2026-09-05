from __future__ import annotations

import os
import shutil
import subprocess
import time

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class HealthSnapshot:
    timestamp: float
    disk_free_gb: float
    trading_mode: str
    live_trading_enabled: bool
    ai_can_execute_live: bool
    status: str
    reasons: list[str]


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() == "true"


def snapshot(path: str = ".") -> HealthSnapshot:
    usage = shutil.disk_usage(path)
    disk_free_gb = usage.free / (1024 ** 3)

    reasons: list[str] = []

    live = _bool("LIVE_TRADING_ENABLED")
    ai_live = _bool("AI_CAN_EXECUTE_LIVE")

    if ai_live:
        reasons.append("AI_CAN_EXECUTE_LIVE_UNSAFE")

    if disk_free_gb < 2:
        reasons.append("LOW_DISK_SPACE")

    status = "PASS" if not reasons else "BLOCK"

    return HealthSnapshot(
        timestamp=time.time(),
        disk_free_gb=round(disk_free_gb, 2),
        trading_mode=os.getenv("TRADING_MODE", "research"),
        live_trading_enabled=live,
        ai_can_execute_live=ai_live,
        status=status,
        reasons=reasons,
    )


def snapshot_dict(path: str = ".") -> dict:
    return asdict(snapshot(path))


def cpu_percent() -> float | None:
    """Return host CPU use normalized across logical CPUs."""
    try:
        output = subprocess.run(["ps", "-A", "-o", "%cpu="], capture_output=True,
                                text=True, timeout=3, check=True).stdout
        return round(min(100.0, sum(float(value) for value in output.split()) /
                         max(1, os.cpu_count() or 1)), 1)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
