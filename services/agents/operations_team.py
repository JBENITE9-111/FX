from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable

from services.agents.supervisor import supervisor

ROOT = Path("/Users/macmac/Documents/Codex/FX")
STATE = ROOT / "data" / "agents" / "operations_team.json"


AGENTS = (
    ("risk_management", "Risk Management", "Exposure, drawdown, protection and kill-switch state"),
    ("anomaly_detection", "Anomaly Detection", "Unexpected bot, signal and execution behavior"),
    ("compliance", "Compliance & Regulation", "Paper/live policy and prohibited execution patterns"),
    ("error_log_parser", "Error Log Parser", "Recent application errors translated into operational state"),
    ("api_connectivity", "API Connectivity", "Market-data and local service connectivity"),
    ("state_verification", "State Verification", "Database, position and journal consistency"),
    ("backtesting_critic", "Backtesting Critic", "OOS, walk-forward and remaining promotion evidence"),
    ("slippage_cost", "Slippage & Cost Analyst", "Recorded costs, slippage and missing execution evidence"),
    ("market_regime", "Market Regime Classifier", "Latest verified regime evidence across favorites"),
    ("static_code_analyzer", "Static Code Analyzer", "Runtime policy and source-tree integrity signals"),
    ("prompt_strategy_refiner", "Prompt / Strategy Refiner", "Evidence gaps and proposed research improvements"),
)


class AutomatedAgentTeam:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._last_run_at: float | None = None
        self._last_error: str | None = None
        self._results: list[dict] = []

    def start(self) -> dict:
        if self._thread and self._thread.is_alive():
            return self.status()
        self._stop.clear()
        self.run_once()
        self._thread = threading.Thread(target=self._loop, name="fx-automated-agent-team", daemon=True)
        self._thread.start()
        return self.status()

    def stop(self) -> None:
        self._stop.set()

    def _snapshot(self) -> dict:
        from backend.app.services.bots.runtime import bots
        from services.bot_signals.store import list_signals
        from services.learning.status import learning_overview
        from services.monitoring.sentinel import sentinel
        from services.operations.store import list_events, list_favorites
        from services.reporting.trade_report import dashboard, trade_rows

        data: dict = {
            "sentinel": sentinel.status(),
            "bots": bots.list(),
            "signals": list_signals(limit=500),
            "learning": learning_overview(),
            "events": list_events(200),
            "favorites": list_favorites(),
        }
        try:
            data["trading"] = dashboard()
            data["canonical_trades"] = trade_rows(limit=5000)
        except Exception as exc:
            data["trading_error"] = type(exc).__name__
        return data

    @staticmethod
    def _result(status: str, summary: str, evidence: list[str], action: str) -> dict:
        return {"status": status, "summary": summary, "evidence": evidence, "recommended_action": action, "automatic_changes": []}

    def _evaluate(self, agent_id: str, data: dict) -> dict:
        sentinel = data["sentinel"]
        trading = data.get("trading") or {}
        account = trading.get("account") or {}
        positions = trading.get("open_positions") or []
        metrics = trading.get("metrics") or {}
        if agent_id == "risk_management":
            equity, exposure = float(account.get("equity") or 0), float(account.get("total_exposure") or 0)
            ratio = exposure / equity if equity > 0 else 0
            limit = float(os.getenv("FX_AGENT_MAX_TOTAL_EXPOSURE_PERCENT", "50")) / 100
            blocked = sentinel.get("status") == "BLOCK" or ratio > limit
            return self._result("BLOCK" if blocked else "PASS", f"{len(positions)} open local-paper positions; total exposure {ratio:.1%} of equity.", ["local_paper.account", "sentinel.status"], "Keep automation blocked." if blocked else "Continue monitoring; deterministic risk remains sovereign.")
        if agent_id == "anomaly_detection":
            running = sum(str(bot.get("status")) == "RUNNING" for bot in data["bots"])
            recent = [event for event in data["events"] if float(event.get("occurred_at") or 0) > time.time() - 3600]
            status = "ATTENTION" if len(recent) > 500 else "PASS"
            return self._result(status, f"{running}/{len(data['bots'])} scanners running; {len(recent)} events in the last hour.", ["bots.runtime", "operations.events"], "Investigate event burst before execution." if status != "PASS" else "Continue rate and duplicate monitoring.")
        if agent_id == "compliance":
            live = os.getenv("AI_CAN_EXECUTE_LIVE", "false").lower() == "true" or os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
            return self._result("BLOCK" if live else "ATTENTION", "Unsafe live flag is enabled." if live else "Autonomous real-money execution is disabled; jurisdiction and venue rule packs are not configured.", ["AI_CAN_EXECUTE_LIVE", "LIVE_TRADING_ENABLED"], "Engage kill switch and restore safe environment." if live else "Keep paper-only policy locked and add jurisdiction-specific rules before any live review.")
        if agent_id == "error_log_parser":
            files = [ROOT / "data/logs/api-error.log", ROOT / "logs/fx-api.log"]
            lines = []
            for path in files:
                if path.exists():
                    lines.extend(path.read_text(errors="replace").splitlines()[-120:])
            errors = [line for line in lines if any(word in line.lower() for word in ("traceback", " error", "exception"))]
            return self._result("ATTENTION" if errors else "PASS", f"{len(errors)} error-like lines found in the recent bounded log window.", [path.name for path in files if path.exists()], "Review the latest error fingerprints; no source files are changed automatically." if errors else "No repair action required.")
        if agent_id == "api_connectivity":
            provider_errors = [event for event in data["events"] if event.get("event_type") == "provider.error" and float(event.get("occurred_at") or 0) > time.time() - 3600]
            return self._result("ATTENTION" if provider_errors else "PASS", f"{len(provider_errors)} provider errors recorded in the last hour.", ["operations.provider.error", "London Strategic Edge"], "Retry safely and inspect provider evidence; never fabricate a quote." if provider_errors else "Continue provider checks.")
        if agent_id == "state_verification":
            db_check = next((item for item in sentinel.get("checks", []) if item.get("name") == "Local paper databases"), {})
            open_trades = [row for row in data.get("canonical_trades", []) if row.get("status") == "OPEN"]
            unprotected = sum(not row.get("stop") or not row.get("profit_plan") for row in open_trades)
            unmatched = abs(len(positions) - len(open_trades))
            status = "BLOCK" if db_check.get("status") == "BLOCK" or unprotected else ("ATTENTION" if unmatched else "PASS")
            return self._result(status, f"Database check {db_check.get('status', 'UNKNOWN')}; {unprotected} canonical open trades lack protection; {unmatched} position/trade records need reconciliation.", ["sentinel.sqlite_quick_check", "local_paper.positions", "journal.canonical_trades"], "Block new execution and reconcile positions." if status == "BLOCK" else ("Reconcile legacy position records with the canonical journal." if unmatched else "State is internally consistent."))
        if agent_id == "backtesting_critic":
            summary = data["learning"]["summary"]
            examining = int(summary.get("examining") or 0)
            return self._result("ATTENTION", f"{summary.get('current_models', 0)} current models; {examining} reached examination; 0 paper eligible.", ["learning.registry", "walk_forward"], "Build calibration, cost stress, stability, Monte Carlo, locked holdout and paper examination evidence.")
        if agent_id == "slippage_cost":
            closed = int(metrics.get("closed_trades") or 0)
            return self._result("ATTENTION" if closed == 0 else "PASS", f"{closed} canonical closed trades available for realized cost analysis.", ["journal.canonical_trades"], "Collect canonical fills, fees and expected-versus-realized prices." if closed == 0 else "Recompute cost and slippage distributions by asset and bot.")
        if agent_id == "market_regime":
            analyses = [event for event in data["events"] if event.get("event_type") == "analysis.completed"]
            regimes = [event.get("payload", {}).get("regime") for event in analyses if event.get("payload", {}).get("regime")]
            return self._result("PASS" if regimes else "UNKNOWN", f"{len(regimes)} explicit regime classifications recorded across {len(analyses)} favorite analyses.", ["operations.analysis.completed"], "Classify per instrument only from fresh verified bars; do not infer regime from a direction label." if analyses else "Run a favorite analysis to create regime evidence.")
        if agent_id == "static_code_analyzer":
            required = [ROOT / "services/risk/decision_contract.py", ROOT / "services/monitoring/sentinel.py", ROOT / "services/events/contracts.py"]
            missing = [path.name for path in required if not path.exists()]
            syntax_ok = False
            if not missing:
                check = subprocess.run([str(ROOT / ".venv-core/bin/python"), "-m", "compileall", "-q", "backend", "services"], cwd=ROOT, capture_output=True, text=True, timeout=60)
                syntax_ok = check.returncode == 0
            return self._result("PASS" if syntax_ok and not missing else "BLOCK", "Required safety modules are present and Python syntax compilation passed." if syntax_ok and not missing else "Required modules are missing or Python compilation failed.", [str(path.relative_to(ROOT)) for path in required], "Source changes still require review, security analysis and test gates.")
        if agent_id == "prompt_strategy_refiner":
            summary = data["learning"]["summary"]
            return self._result("ATTENTION", f"{summary.get('validation_blocked', 0)} models need revised hypotheses or evidence; automatic prompt or strategy mutation is disabled.", ["learning.blocked_at", "strategy_promotion_policy"], "Propose one versioned challenger experiment; require validation before adoption.")
        raise ValueError(f"Unknown automated agent {agent_id}")

    def run_once(self) -> dict:
        if not self._lock.acquire(blocking=False):
            return self.status()
        try:
            data = self._snapshot()
            results = []
            for agent_id, name, description in AGENTS:
                run = supervisor.run(agent_id=agent_id, goal=description, task=lambda checkpoint, key=agent_id: self._evaluate(key, data))
                result = {"agent_id": agent_id, "name": name, "description": description, "run_id": run.run_id, "run_status": run.status, **run.result}
                if run.error:
                    result.update({"status": "ERROR", "summary": run.error, "recommended_action": "Inspect the agent failure.", "evidence": []})
                results.append(result)
            self._results, self._last_run_at, self._last_error = results, time.time(), None
            STATE.parent.mkdir(parents=True, exist_ok=True)
            STATE.write_text(json.dumps(self.status(), indent=2, default=str))
        except Exception as exc:
            self._last_error = f"{type(exc).__name__}: {str(exc)[:200]}"
        finally:
            self._lock.release()
        return self.status()

    def _loop(self) -> None:
        interval = max(60, int(os.getenv("FX_AGENT_TEAM_INTERVAL_SECONDS", "300")))
        while not self._stop.wait(interval):
            self.run_once()

    def status(self) -> dict:
        running = bool(self._thread and self._thread.is_alive())
        blocked = sum(item.get("status") == "BLOCK" for item in self._results)
        return {
            "status": "BLOCK" if blocked else ("DEGRADED" if self._last_error else "HEALTHY"),
            "running": running,
            "autopilot": True,
            "paper_only": True,
            "kill_switch": "ENGAGED" if blocked else "CLEAR",
            "last_run_at": self._last_run_at,
            "next_interval_seconds": max(60, int(os.getenv("FX_AGENT_TEAM_INTERVAL_SECONDS", "300"))),
            "last_error": self._last_error,
            "agents": list(self._results),
            "policy": "Agents may monitor, diagnose and recommend. They cannot enable live trading, raise risk, rewrite production strategies or self-promote models.",
        }


operations_team = AutomatedAgentTeam()
