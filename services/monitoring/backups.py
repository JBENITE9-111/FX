from __future__ import annotations

import sqlite3
import time
from pathlib import Path

ROOT = Path("/Users/macmac/Documents/Codex/FX")
BACKUP_ROOT = ROOT / "backups" / "sqlite"


def backup_databases(*, max_age_days: int = 30) -> dict:
    started = time.time()
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(started))
    destination = BACKUP_ROOT / stamp
    copied, failures = [], []
    for source in (ROOT / "data").rglob("*.sqlite3"):
        relative = source.relative_to(ROOT / "data")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(source, timeout=5) as original, sqlite3.connect(target) as backup:
                original.backup(backup)
            copied.append(str(relative))
        except sqlite3.Error as exc:
            failures.append({"database": str(relative), "error_type": type(exc).__name__})
    cutoff = started - max_age_days * 86400
    if BACKUP_ROOT.exists():
        for directory in BACKUP_ROOT.iterdir():
            if directory.is_dir() and directory.stat().st_mtime < cutoff:
                for child in sorted(directory.rglob("*"), reverse=True):
                    if child.is_file():
                        child.unlink()
                    elif child.is_dir():
                        child.rmdir()
                directory.rmdir()
    return {"status": "PASS" if not failures else "DEGRADED", "timestamp": started,
            "destination": str(destination), "databases": copied, "failures": failures}
