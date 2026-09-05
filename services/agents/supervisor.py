from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path("/Users/macmac/Documents/Codex/FX")
DB = ROOT / "data" / "agents" / "agents.sqlite3"

@dataclass
class AgentRun:
    run_id: str
    agent_id: str
    goal: str
    status: str
    started_at: float
    updated_at: float
    completed_at: float | None = None
    checkpoint: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

class AgentSupervisor:
    def __init__(self):
        DB.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_runs(
                    run_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    completed_at REAL,
                    checkpoint_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    error TEXT
                )
                """
            )

    def _save(self, run: AgentRun) -> None:
        with sqlite3.connect(DB) as conn:
            conn.execute(
                """
                INSERT INTO agent_runs(
                    run_id,agent_id,goal,status,started_at,updated_at,
                    completed_at,checkpoint_json,result_json,error
                )
                VALUES(?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status=excluded.status,
                    updated_at=excluded.updated_at,
                    completed_at=excluded.completed_at,
                    checkpoint_json=excluded.checkpoint_json,
                    result_json=excluded.result_json,
                    error=excluded.error
                """,
                (
                    run.run_id,
                    run.agent_id,
                    run.goal,
                    run.status,
                    run.started_at,
                    run.updated_at,
                    run.completed_at,
                    json.dumps(run.checkpoint, default=str),
                    json.dumps(run.result, default=str),
                    run.error,
                ),
            )

    def run(
        self,
        *,
        agent_id: str,
        goal: str,
        task: Callable[[Callable[[dict[str, Any]], None]], dict[str, Any]],
    ) -> AgentRun:
        now = time.time()
        run = AgentRun(
            run_id=str(uuid.uuid4()),
            agent_id=agent_id,
            goal=goal,
            status="RUNNING",
            started_at=now,
            updated_at=now,
        )
        self._save(run)

        def checkpoint(value: dict[str, Any]) -> None:
            run.checkpoint = value
            run.updated_at = time.time()
            self._save(run)

        try:
            result = task(checkpoint)
            run.result = result
            run.status = "COMPLETE"
            run.completed_at = time.time()
            run.updated_at = run.completed_at
        except Exception as exc:
            run.status = "FAILED"
            run.error = str(exc)
            run.completed_at = time.time()
            run.updated_at = run.completed_at

        self._save(run)
        return run

    def latest(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(DB) as conn:
            rows = conn.execute(
                """
                SELECT run_id,agent_id,goal,status,started_at,updated_at,
                       completed_at,checkpoint_json,result_json,error
                FROM agent_runs
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        result = []
        for row in rows:
            result.append(
                {
                    "run_id": row[0],
                    "agent_id": row[1],
                    "goal": row[2],
                    "status": row[3],
                    "started_at": row[4],
                    "updated_at": row[5],
                    "completed_at": row[6],
                    "checkpoint": json.loads(row[7]),
                    "result": json.loads(row[8]),
                    "error": row[9],
                }
            )
        return result

supervisor = AgentSupervisor()
