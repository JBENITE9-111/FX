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
    """Semantic FX memory.

    Raw prices/bars do NOT belong here. Keep those in Parquet/DuckDB.
    This index stores compressed embeddings for semantic retrieval.
    """

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
            self.meta: dict[str, dict] = json.loads(self.meta_path.read_text())
        else:
            self.meta = {}

    def add(self, record: MemoryRecord, embedding: np.ndarray) -> None:
        vec = np.asarray(embedding, dtype=np.float32).reshape(1, self.dim)
        ids = np.asarray([record.id], dtype=np.uint64)
        with self._lock:
            # Remove same stable id before replacement.
            if str(record.id) in self.meta:
                try:
                    self.index.remove(record.id)
                except Exception:
                    pass
            self.index.add_with_ids(vec, ids)
            self.meta[str(record.id)] = asdict(record)

    def remove(self, record_id: int) -> None:
        with self._lock:
            self.index.remove(record_id)
            self.meta.pop(str(record_id), None)

    def search(
        self,
        query_embedding: np.ndarray,
        *,
        k: int = 10,
        allow_ids: list[int] | None = None,
    ) -> list[dict]:
        q = np.asarray(query_embedding, dtype=np.float32).reshape(1, self.dim)
        allow = None
        if allow_ids is not None:
            allow = np.asarray(allow_ids, dtype=np.uint64)

        with self._lock:
            scores, ids = self.index.search(q, k=k, allowlist=allow)

        score_row = np.asarray(scores).reshape(-1)
        id_row = np.asarray(ids).reshape(-1)
        out = []
        for score, rid in zip(score_row.tolist(), id_row.tolist()):
            meta = self.meta.get(str(int(rid)))
            if meta:
                out.append({"score": float(score), **meta})
        return out

    def filter_ids(self, predicate: Callable[[dict], bool]) -> list[int]:
        return [int(k) for k, v in self.meta.items() if predicate(v)]

    def sync(self) -> None:
        with self._lock:
            self.index.sync(str(self.path))
            tmp = self.meta_path.with_suffix(self.meta_path.suffix + ".tmp")
            tmp.write_text(json.dumps(self.meta, separators=(",", ":"), sort_keys=True))
            os.replace(tmp, self.meta_path)


_singleton: TurboVecMemory | None = None


def get_memory_store() -> TurboVecMemory:
    global _singleton
    if _singleton is None:
        _singleton = TurboVecMemory(
            dim=int(os.getenv("FX_MEMORY_DIM", "384")),
            bit_width=int(os.getenv("FX_MEMORY_BITS", "4")),
            path=os.getenv("FX_MEMORY_PATH", "data/memory/fx_memory.tvim"),
        )
    return _singleton
