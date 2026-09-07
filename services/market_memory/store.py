from __future__ import annotations

import io
import json
import os
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from services.market_memory.quality import normalize_and_validate_bars
from services.market_memory.registry import HistoricalRegistry
from services.market_memory.schema import (
    BAR_SCHEMA_VERSION,
    git_commit,
    sha256_bytes,
    slug,
    stable_id,
    stable_json,
    utc_now,
)


ROOT = Path("/Users/macmac/Documents/Codex/FX")


class MarketMemoryStore:
    def __init__(self, root: Path | None = None, project_root: Path = ROOT):
        self.project_root = project_root
        self.root = root or project_root / "data" / "historical"
        self.registry = HistoricalRegistry(self.root / "registry.sqlite3")

    @staticmethod
    def _relative(path: Path, root: Path) -> str:
        return str(path.resolve().relative_to(root.resolve()))

    def _check_budget(self, expected_bytes: int) -> None:
        max_bytes = int(os.getenv("FX_HISTORY_MAX_INGEST_BYTES", str(256 * 1024 * 1024)))
        min_free = int(os.getenv("FX_HISTORY_MIN_FREE_BYTES", str(5 * 1024 * 1024 * 1024)))
        free = shutil.disk_usage(self.root.parent).free
        if expected_bytes > max_bytes:
            raise ValueError(
                f"Historical ingest estimate {expected_bytes} exceeds the per-run budget {max_bytes}."
            )
        if free - expected_bytes < min_free:
            raise ValueError(
                "Historical ingest refused because it would violate the free-disk reserve."
            )

    @staticmethod
    def _write_immutable(path: Path, payload: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if sha256_bytes(path.read_bytes()) != sha256_bytes(payload):
                raise RuntimeError(f"Immutable historical artifact collision: {path}")
            return
        temporary = path.with_suffix(path.suffix + ".partial")
        temporary.write_bytes(payload)
        os.chmod(temporary, 0o600)
        temporary.replace(path)

    def register_lse_source(self) -> dict[str, Any]:
        return self.registry.insert_source({
            "source_id": "london-strategic-edge",
            "provider": "London Strategic Edge",
            "authority": "PRIMARY_RESEARCH_PROVIDER",
            "license_class": "PRIVATE_PROVIDER_TERMS",
            "local_storage_allowed": "VERIFY_PROVIDER_TERMS",
            "redistribution_allowed": "NO",
            "notes": (
                "Personal local research only. Retention and derived-use rights must be "
                "checked against the owner's provider agreement before expansion or redistribution."
            ),
            "metadata": {"execution_authority": False, "paper_research_only": True},
        })

    def ingest_bars(
        self,
        *,
        rows: list[dict[str, Any]],
        provider: str,
        source_id: str,
        dataset_name: str,
        symbol: str,
        asset_class: str,
        timeframe: str,
        venue: str | None = None,
        adjustment_policy: str = "PROVIDER_UNSPECIFIED",
        parent_artifact_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if source_id == "london-strategic-edge":
            self.register_lse_source()
        elif not any(row["source_id"] == source_id for row in self.registry.list_sources()):
            raise ValueError("Register source licensing metadata before ingesting its data.")

        source_rows = [dict(row) for row in rows]
        raw_payload = (
            "\n".join(stable_json(row) for row in source_rows) + "\n"
        ).encode()
        self._check_budget(len(raw_payload) * 2)

        frame, quality = normalize_and_validate_bars(source_rows)
        parquet_buffer = io.BytesIO()
        frame.to_parquet(parquet_buffer, index=False, compression="zstd")
        curated_payload = parquet_buffer.getvalue()
        self._check_budget(len(raw_payload) + len(curated_payload))

        dataset_identity = {
            "source_id": source_id,
            "dataset_name": dataset_name,
            "symbol": symbol,
            "asset_class": asset_class,
            "venue": venue,
            "timeframe": timeframe,
            "schema_version": BAR_SCHEMA_VERSION,
            "adjustment_policy": adjustment_policy,
        }
        dataset_id = stable_id("dataset", dataset_identity)
        created_at = utc_now()
        self.registry.insert_dataset({
            "dataset_id": dataset_id,
            **dataset_identity,
            "created_at": created_at,
        })

        raw_hash = sha256_bytes(raw_payload)
        curated_hash = sha256_bytes(curated_payload)
        artifact_id = stable_id("artifact", {
            "dataset_id": dataset_id,
            "curated_sha256": curated_hash,
            "parent_artifact_ids": sorted(parent_artifact_ids or []),
        })
        partition = Path(slug(provider), slug(dataset_name), slug(symbol), slug(timeframe))
        raw_path = self.root / "raw" / partition / f"{raw_hash}.jsonl"
        curated_path = self.root / "curated" / partition / f"{curated_hash}.parquet"
        manifest_path = self.root / "manifests" / f"{artifact_id}.json"
        already_present = manifest_path.exists()
        self._write_immutable(raw_path, raw_payload)
        self._write_immutable(curated_path, curated_payload)
        if already_present:
            existing_manifest = json.loads(manifest_path.read_text())
            existing_record = self.registry.get_artifact(artifact_id)
            if not existing_record:
                raise RuntimeError(
                    "Historical manifest exists without its registry record."
                )
            return {
                "manifest": existing_manifest,
                "registry": existing_record,
                "deduplicated": True,
            }

        manifest = {
            "artifact_id": artifact_id,
            "dataset_id": dataset_id,
            "provider": provider,
            **dataset_identity,
            "coverage_start": quality["coverage_start"],
            "coverage_end": quality["coverage_end"],
            "rows": quality["rows"],
            "size_bytes": len(raw_payload) + len(curated_payload),
            "raw_sha256": raw_hash,
            "curated_sha256": curated_hash,
            "raw_path": self._relative(raw_path, self.project_root),
            "curated_path": self._relative(curated_path, self.project_root),
            "manifest_path": self._relative(manifest_path, self.project_root),
            "quality": quality,
            "parent_artifact_ids": sorted(parent_artifact_ids or []),
            "git_commit": git_commit(self.project_root),
            "created_at": created_at,
            "immutable": True,
            "research_only": True,
        }
        manifest_payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        self._write_immutable(manifest_path, manifest_payload)
        record = self.registry.insert_artifact({
            key: manifest[key] for key in (
                "artifact_id", "dataset_id", "raw_sha256", "curated_sha256",
                "raw_path", "curated_path", "manifest_path", "coverage_start",
                "coverage_end", "rows", "size_bytes", "parent_artifact_ids",
                "git_commit", "created_at",
            )
        } | {
            "quality_score": quality["quality_score"],
            "validation_status": quality["status"],
        })
        return {"manifest": manifest, "registry": record, "deduplicated": already_present}

    def load_artifact(self, artifact_id: str) -> tuple[pd.DataFrame, dict[str, Any]]:
        record = self.registry.get_artifact(artifact_id)
        if not record:
            raise KeyError(f"Unknown historical artifact: {artifact_id}")
        path = self.project_root / record["curated_path"]
        payload = path.read_bytes()
        if sha256_bytes(payload) != record["curated_sha256"]:
            raise RuntimeError("Historical artifact checksum verification failed.")
        manifest = json.loads((self.project_root / record["manifest_path"]).read_text())
        return pd.read_parquet(io.BytesIO(payload)), manifest
