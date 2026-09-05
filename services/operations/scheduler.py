from __future__ import annotations

import threading
import time
import asyncio

from services.monitoring.sentinel import sentinel
from services.operations.notifications import process_due_deliveries, route_event
from services.operations.reports import generate_report
from services.operations.store import claim_due_schedules, finish_schedule, get_favorite, record_event


class PersistentScheduler:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_error: str | None = None
        self._last_tick: float | None = None

    def start(self) -> dict:
        if self._thread and self._thread.is_alive():
            return self.status()
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="fx-persistent-scheduler", daemon=True)
        self._thread.start()
        return self.status()

    def stop(self) -> None:
        self._stop.set()

    def status(self) -> dict:
        return {"status": "HEALTHY" if self._thread and self._thread.is_alive() and not self._last_error else "DEGRADED",
                "running": bool(self._thread and self._thread.is_alive()), "runtime": "LOCAL",
                "last_tick": self._last_tick, "last_error": self._last_error,
                "detail": "Schedules run only while this Mac and FX are running."}

    def run_due_once(self) -> int:
        self._last_tick = time.time()
        processed = 0
        for schedule in claim_due_schedules():
            report_id = event_id = None
            try:
                favorite = get_favorite(schedule["favorite_id"]) if schedule.get("favorite_id") else None
                subject = favorite["favorite_id"] if favorite else "fx-system"
                if schedule["action"] == "analyze_favorite" and favorite:
                    # Import after application startup to avoid coupling the store
                    # to the FastAPI route graph.
                    from backend.app.routes.fx_operations import run_favorite
                    result = asyncio.run(run_favorite(subject))
                    event_id = (result.get("event") or {}).get("event_id")
                    summary = f"{favorite['symbol']} · {result.get('state', 'UNKNOWN')}"
                    finish_schedule(schedule, status="COMPLETE" if result.get("ok") else "FAILED",
                                    summary=summary, event_id=event_id)
                elif schedule["action"] == "generate_report":
                    report = generate_report("favorite" if favorite else "system", subject)
                    report_id = report["report_id"]
                    event = record_event(event_type="report.generated", source="persistent_scheduler",
                                         subject_type="favorite" if favorite else "system", subject_id=subject,
                                         state="RESEARCH_COMPLETE", payload={"report_id": report_id, "title": report["title"]},
                                         evidence_ids=report["evidence_ids"], versions={"scheduler": "1", "report": report["report_version"]},
                                         input_hash=report["input_hash"], dedup_key=f"report:{schedule['schedule_id']}:{int(time.time() // (schedule['interval_minutes'] * 60))}")
                    event_id = event["event_id"]
                    route_event(event, channels=schedule["channels"], message=f"{report['title']}\n{report['status']}\nResearch and paper only.")
                    finish_schedule(schedule, status="COMPLETE", summary=report["title"], event_id=event_id, report_id=report_id)
                else:
                    raise ValueError("Unsupported scheduler action")
            except Exception as exc:
                self._last_error = f"{type(exc).__name__}: {str(exc)[:160]}"
                finish_schedule(schedule, status="FAILED", summary=self._last_error, event_id=event_id, report_id=report_id)
            processed += 1
        process_due_deliveries()
        if processed and not self._last_error:
            self._last_error = None
        return processed

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                health = sentinel.status()
                blocked = health.get("status") == "BLOCK"
                if not blocked:
                    self.run_due_once()
            except Exception as exc:
                self._last_error = f"{type(exc).__name__}: {str(exc)[:160]}"
            self._stop.wait(15)


scheduler = PersistentScheduler()
