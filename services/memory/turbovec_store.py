from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from turbovec import IdMapIndex

@dataclass
class MemoryRecord:
    id: int
    kind: str
    text: str
    instrument: str | None = None
    strategy_id: str | None = None
    timeframe: str | None = None
    regime: str | None = None
    timestamp: float | None = None
    outcome: str | None = None

class TurboVecMemory:
    def __init__(self, dim: int, path: str, bit_width: int = 4):
        self.dim = dim
        self.path = Path(path)
        self.meta_path = self.path.with_suffix(self.path.suffix + ".json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

        if self.path.exists():
            self.index = IdMapIndex.load(str(self.path))
        else:
            self.index = IdMapIndex(dim=dim, bit_width=bit_width)

        if self.meta_path.exists():
            self.meta = json.loads(self.meta_path.read_text())
        else:
            self.meta = {}

    def add(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        vector = np.asarray(
            embedding,
            dtype=np.float32,
        ).reshape(1, self.dim)

        ids = np.asarray([record.id], dtype=np.uint64)

        with self._lock:
            if str(record.id) in self.meta:
                try:
                    self.index.remove(record.id)
                except Exception:
                    pass

            self.index.add_with_ids(vector, ids)
            self.meta[str(record.id)] = asdict(record)

    def search(
        self,
        query_embedding: np.ndarray,
        *,
        k: int = 10,
        allow_ids: list[int] | None = None,
    ) -> list[dict]:
        query = np.asarray(
            query_embedding,
            dtype=np.float32,
        ).reshape(1, self.dim)

        allowlist = (
            np.asarray(allow_ids, dtype=np.uint64)
            if allow_ids is not None
            else None
        )

        with self._lock:
            scores, ids = self.index.search(
                query,
                k=k,
                allowlist=allowlist,
            )

        results = []
        for score, record_id in zip(
            np.asarray(scores).reshape(-1).tolist(),
            np.asarray(ids).reshape(-1).tolist(),
        ):
            metadata = self.meta.get(str(int(record_id)))
            if metadata:
                results.append(
                    {
                        "score": float(score),
                        **metadata,
                    }
                )

        return results

    def filter_ids(
        self,
        predicate: Callable[[dict], bool],
    ) -> list[int]:
        return [
            int(record_id)
            for record_id, metadata in self.meta.items()
            if predicate(metadata)
        ]

    def sync(self) -> None:
        with self._lock:
            self.index.sync(str(self.path))

            temp = self.meta_path.with_suffix(
                self.meta_path.suffix + ".tmp"
            )

            temp.write_text(
                json.dumps(
                    self.meta,
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )

            os.replace(temp, self.meta_path)
