from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.app.services.training.trainer import load_registry, train_all
from services.instruments.training_universe import universe

ROOT = Path("/Users/macmac/Documents/Codex/FX")
STATE_PATH = ROOT / "data" / "learning" / "continuous_state.json"


class ContinuousLearningController:
    def __init__(self):
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._state = self._load()
        self._state.update({"status": "STOPPED", "current": None})
        self._save()

    def _load(self) -> dict:
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            return {}

    def _save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp = STATE_PATH.with_suffix(".tmp")
        temp.write_text(json.dumps(self._state, indent=2, default=str))
        temp.replace(STATE_PATH)

    def _update(self, **changes) -> None:
        with self._lock:
            self._state.update(changes)
            self._state["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save()

    def status(self) -> dict:
        with self._lock:
            try:
                load_1m = round(os.getloadavg()[0], 2)
            except (AttributeError, OSError):
                load_1m = None
            cpu_percent = self._cpu_percent()
            public = {
                key: value for key, value in self._state.items()
                if key != "diagnostic" and not key.startswith("_")
            }
            return {
                **public,
                "worker_alive": bool(self._thread and self._thread.is_alive()),
                "universe_size": len(universe()),
                "research_only": True,
                "production_mutation": False,
                "load_1m": load_1m,
                "max_load": float(os.getenv("FX_TRAINING_MAX_LOAD", "6.0")),
                "resource_retry_seconds": int(os.getenv("FX_TRAINING_RESOURCE_RETRY_SECONDS", "30")),
                "failed_target_retry_seconds": int(os.getenv("FX_FAILED_TRAINING_RETRY_SECONDS", "21600")),
                "pause_reason": (
                    "CPU use is above the configured safe training limit. The worker remains alive and retries automatically."
                    if self._state.get("status") == "PAUSED_RESOURCE_PRESSURE" else None
                ),
                "cpu_percent": cpu_percent,
                "max_cpu_percent": float(os.getenv("FX_TRAINING_MAX_CPU_PERCENT", "85")),
            }

    def start(self, source: str = "USER") -> dict:
        with self._lock:
            if self._thread and self._thread.is_alive():
                return {**self._state, "worker_alive": True, "universe_size": len(universe())}
            self._stop.clear()
            self._state.update({"status": "RUNNING", "started_by": source, "started_at": datetime.now(timezone.utc).isoformat(), "last_error": None})
            self._save()
            self._thread = threading.Thread(target=self._run, name="fx-continuous-learning", daemon=True)
            self._thread.start()
        return self.status()

    def stop(self) -> dict:
        self._stop.set()
        self._update(status="STOPPING")
        return self.status()

    def _recently_trained(self, target: dict) -> bool:
        minimum_age = float(os.getenv("FX_MIN_RETRAIN_SECONDS", "86400"))
        matching = [
            item for item in load_registry().values()
            if item.get("symbol") == target["symbol"]
            and item.get("timeframe") == target["timeframe"]
            and int(item.get("horizon", -1)) == target["horizon"]
        ]
        if not matching:
            return False
        latest = max(str(item.get("trained_at") or "") for item in matching)
        try:
            age = time.time() - datetime.fromisoformat(latest).timestamp()
            return age < minimum_age
        except ValueError:
            return False

    @staticmethod
    def _target_key(target: dict) -> str:
        return f"{target['symbol']}|{target['timeframe']}|{target['horizon']}"

    def _failed_recently(self, target: dict) -> bool:
        retry_after = float(os.getenv("FX_FAILED_TRAINING_RETRY_SECONDS", "21600"))
        entry = (self._state.get("_failed_targets") or {}).get(self._target_key(target)) or {}
        return time.time() - float(entry.get("attempted_at") or 0) < retry_after

    @staticmethod
    def _cpu_percent() -> float | None:
        try:
            output = subprocess.run(
                ["ps", "-A", "-o", "%cpu="], capture_output=True, text=True, timeout=3, check=True
            ).stdout
            total = sum(float(value) for value in output.split())
            return round(min(100.0, total / max(1, os.cpu_count() or 1)), 1)
        except (OSError, ValueError, subprocess.SubprocessError):
            return None

    def _resource_pressure(self) -> bool:
        cpu = self._cpu_percent()
        return cpu is not None and cpu > float(os.getenv("FX_TRAINING_MAX_CPU_PERCENT", "85"))

    def _run(self) -> None:
        completed = int(self._state.get("completed_jobs", 0))
        failed = int(self._state.get("failed_jobs", 0))
        while not self._stop.is_set():
            did_work = False
            for target in universe():
                if self._stop.is_set():
                    break
                retry_seconds = int(os.getenv("FX_TRAINING_RESOURCE_RETRY_SECONDS", "30"))
                while self._resource_pressure() and not self._stop.wait(retry_seconds):
                    self._update(status="PAUSED_RESOURCE_PRESSURE", current=None)
                if self._stop.is_set():
                    break
                if self._recently_trained(target) or self._failed_recently(target):
                    continue
                did_work = True
                self._update(status="RUNNING", current=target, stage="FETCHING_AND_TRAINING")
                try:
                    result = train_all(target["symbol"], target["timeframe"], target["horizon"])
                    completed += 1
                    failed_targets = dict(self._state.get("_failed_targets") or {})
                    failed_targets.pop(self._target_key(target), None)
                    self._update(completed_jobs=completed, last_completed=target, last_result={
                        "elapsed_seconds": result.get("elapsed_seconds"),
                        "models": len(result.get("models", [])),
                    }, _failed_targets=failed_targets, current=None, stage="VALIDATION_RECORDED")
                except Exception as exc:
                    failed += 1
                    failed_targets = dict(self._state.get("_failed_targets") or {})
                    previous = failed_targets.get(self._target_key(target)) or {}
                    failed_targets[self._target_key(target)] = {
                        "attempted_at": time.time(),
                        "attempts": int(previous.get("attempts") or 0) + 1,
                        "error_type": type(exc).__name__,
                    }
                    self._update(
                        failed_jobs=failed,
                        last_failed=target,
                        last_error="This training target could not be completed. FX will retry after the waiting period.",
                        diagnostic={"type": type(exc).__name__, "message": str(exc)},
                        _failed_targets=failed_targets,
                        current=None,
                        stage="JOB_FAILED",
                    )
                if self._stop.wait(float(os.getenv("FX_LEARNING_BETWEEN_JOBS_SECONDS", "30"))):
                    break
            self._update(status="WAITING_FOR_NEW_DATA", current=None, stage="IDLE")
            wait = 300 if did_work else float(os.getenv("FX_LEARNING_IDLE_SECONDS", "1800"))
            self._stop.wait(wait)
        self._update(status="STOPPED", current=None, stage="IDLE")


continuous_learning = ContinuousLearningController()
