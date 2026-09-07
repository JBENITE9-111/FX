from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class HistoricalRegistry:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                PRAGMA foreign_keys=ON;
                CREATE TABLE IF NOT EXISTS sources(
                    source_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    authority TEXT NOT NULL,
                    license_class TEXT NOT NULL,
                    local_storage_allowed TEXT NOT NULL,
                    redistribution_allowed TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS datasets(
                    dataset_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL REFERENCES sources(source_id),
                    dataset_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    asset_class TEXT NOT NULL,
                    venue TEXT,
                    timeframe TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    adjustment_policy TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts(
                    artifact_id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
                    raw_sha256 TEXT NOT NULL,
                    curated_sha256 TEXT NOT NULL,
                    raw_path TEXT NOT NULL,
                    curated_path TEXT NOT NULL,
                    manifest_path TEXT NOT NULL,
                    coverage_start TEXT NOT NULL,
                    coverage_end TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    quality_score REAL NOT NULL,
                    validation_status TEXT NOT NULL,
                    parent_artifact_ids_json TEXT NOT NULL,
                    git_commit TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(dataset_id, curated_sha256)
                );
                CREATE INDEX IF NOT EXISTS idx_artifacts_dataset_created
                    ON artifacts(dataset_id, created_at DESC);
                CREATE TABLE IF NOT EXISTS experiments(
                    experiment_id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
                    strategy_id TEXT NOT NULL,
                    strategy_version TEXT NOT NULL,
                    manifest_path TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _row(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        value = dict(row)
        for key in ("metadata_json", "parent_artifact_ids_json"):
            if key in value:
                value[key.removesuffix("_json")] = json.loads(value.pop(key))
        return value

    def insert_source(self, record: dict[str, Any]) -> dict[str, Any]:
        values = (
            record["source_id"], record["provider"], record["authority"],
            record["license_class"], record["local_storage_allowed"],
            record["redistribution_allowed"], record["notes"],
            json.dumps(record.get("metadata", {}), sort_keys=True),
        )
        with self.connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO sources VALUES(?,?,?,?,?,?,?,?)", values
            )
            row = connection.execute(
                "SELECT * FROM sources WHERE source_id=?", (record["source_id"],)
            ).fetchone()
        return self._row(row) or {}

    def insert_dataset(self, record: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO datasets VALUES(?,?,?,?,?,?,?,?,?,?)",
                tuple(record[key] for key in (
                    "dataset_id", "source_id", "dataset_name", "symbol",
                    "asset_class", "venue", "timeframe", "schema_version",
                    "adjustment_policy", "created_at",
                )),
            )
            row = connection.execute(
                "SELECT * FROM datasets WHERE dataset_id=?", (record["dataset_id"],)
            ).fetchone()
        return self._row(row) or {}

    def insert_artifact(self, record: dict[str, Any]) -> dict[str, Any]:
        values = tuple(record[key] for key in (
            "artifact_id", "dataset_id", "raw_sha256", "curated_sha256",
            "raw_path", "curated_path", "manifest_path", "coverage_start",
            "coverage_end", "rows", "size_bytes", "quality_score",
            "validation_status",
        )) + (
            json.dumps(record.get("parent_artifact_ids", []), sort_keys=True),
            record.get("git_commit"), record["created_at"],
        )
        with self.connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                values,
            )
            row = connection.execute(
                "SELECT * FROM artifacts WHERE artifact_id=?", (record["artifact_id"],)
            ).fetchone()
        return self._row(row) or {}

    def insert_experiment(self, record: dict[str, Any]) -> dict[str, Any]:
        with self.connect() as connection:
            connection.execute(
                "INSERT OR IGNORE INTO experiments VALUES(?,?,?,?,?,?,?,?)",
                tuple(record[key] for key in (
                    "experiment_id", "artifact_id", "strategy_id",
                    "strategy_version", "manifest_path", "input_hash", "status",
                    "created_at",
                )),
            )
            row = connection.execute(
                "SELECT * FROM experiments WHERE experiment_id=?",
                (record["experiment_id"],),
            ).fetchone()
        return self._row(row) or {}

    def list_sources(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM sources ORDER BY provider").fetchall()
        return [self._row(row) or {} for row in rows]

    def list_datasets(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """SELECT d.*, COUNT(a.artifact_id) AS artifact_count,
                          MAX(a.coverage_end) AS latest_coverage_end
                   FROM datasets d LEFT JOIN artifacts a USING(dataset_id)
                   GROUP BY d.dataset_id ORDER BY d.asset_class,d.symbol,d.timeframe"""
            ).fetchall()
        return [self._row(row) or {} for row in rows]

    def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM artifacts WHERE artifact_id=?", (artifact_id,)
            ).fetchone()
        return self._row(row)

    def latest_artifact(self, dataset_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM artifacts WHERE dataset_id=? ORDER BY created_at DESC LIMIT 1",
                (dataset_id,),
            ).fetchone()
        return self._row(row)
