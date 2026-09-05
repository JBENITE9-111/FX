from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from services.auth.totp import totp_service
from services.monitoring.system_health import cpu_percent, snapshot_dict
from services.monitoring.backups import backup_databases

ROOT = Path("/Users/macmac/Documents/Codex/FX")
STATE = ROOT / "data" / "monitoring" / "sentinel.json"


class HealthSecuritySentinel:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._state: dict = {"status": "STOPPED", "checks": []}
        self._last_backup: dict = {}

    def _check(self) -> dict:
        checks = []
        health = snapshot_dict(str(ROOT))
        checks.append({"name": "Live execution policy", "status": "PASS" if not health["ai_can_execute_live"] else "BLOCK", "detail": "AI_CAN_EXECUTE_LIVE is disabled" if not health["ai_can_execute_live"] else "Unsafe AI live execution flag is enabled"})
        checks.append({"name": "Disk capacity", "status": "PASS" if health["disk_free_gb"] >= 2 else "BLOCK", "detail": f'{health["disk_free_gb"]:.2f} GB free'})
        checks.append({"name": "Two-factor authentication", "status": "PASS" if totp_service.is_enrolled() else "ACTION", "detail": "Google Authenticator compatible TOTP enrolled" if totp_service.is_enrolled() else "Enrollment is required to activate the app access gate"})
        env_path = ROOT / ".env"
        mode = env_path.stat().st_mode & 0o777 if env_path.exists() else 0
        checks.append({"name": "Secrets file permissions", "status": "PASS" if not mode or mode & 0o077 == 0 else "WARN", "detail": "Restricted to this user" if not mode or mode & 0o077 == 0 else f"Permissions are {mode:o}; expected 600"})
        db_files = list((ROOT / "data").rglob("*.sqlite3"))
        corrupt = []
        for path in db_files:
            try:
                with sqlite3.connect(path, timeout=2) as connection:
                    if connection.execute("PRAGMA quick_check").fetchone()[0] != "ok": corrupt.append(path.name)
            except sqlite3.Error:
                corrupt.append(path.name)
        checks.append({"name": "Local paper databases", "status": "PASS" if not corrupt else "BLOCK", "detail": f"{len(db_files)} SQLite files checked" if not corrupt else "Integrity failure: " + ", ".join(corrupt)})
        cpu = cpu_percent()
        cpu_limit = float(os.getenv("FX_TRAINING_MAX_CPU_PERCENT", "85"))
        checks.append({"name": "System resource pressure", "status": "WARN" if cpu is None or cpu > cpu_limit else "PASS", "detail": "CPU use unavailable" if cpu is None else f"CPU use {cpu:.1f}%; training limit {cpu_limit:.0f}%"})
        overall = "BLOCK" if any(c["status"] == "BLOCK" for c in checks) else ("ATTENTION" if any(c["status"] in {"WARN", "ACTION"} for c in checks) else "PASS")
        return {"status": overall, "running": True, "checked_at": datetime.now(timezone.utc).isoformat(), "checks": checks, "autopilot": True, "can_change_risk_controls": False}

    def run_once(self) -> dict:
        if not self._last_backup or time.time() - float(self._last_backup.get("timestamp", 0)) >= 21600:
            self._last_backup = backup_databases()
        self._state = self._check()
        self._state["backup"] = self._last_backup
        STATE.parent.mkdir(parents=True, exist_ok=True)
        temp = STATE.with_suffix(".tmp")
        temp.write_text(json.dumps(self._state, indent=2))
        temp.replace(STATE)
        return dict(self._state)

    def start(self) -> dict:
        if self._thread and self._thread.is_alive():
            return self.status()
        self._stop.clear()
        self.run_once()
        self._thread = threading.Thread(target=self._loop, name="fx-health-security-sentinel", daemon=True)
        self._thread.start()
        return self.status()

    def _loop(self) -> None:
        while not self._stop.wait(float(os.getenv("FX_SENTINEL_INTERVAL_SECONDS", "60"))):
            self.run_once()

    def stop(self) -> None:
        self._stop.set()

    def status(self) -> dict:
        return {**self._state, "running": bool(self._thread and self._thread.is_alive())}


sentinel = HealthSecuritySentinel()
