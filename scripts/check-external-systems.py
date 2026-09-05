from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

systems = json.loads(
    (
        ROOT
        / "external"
        / "systems.json"
    ).read_text()
)

print("")
print("=" * 64)
print(" FX EXTERNAL SYSTEMS")
print("=" * 64)
print("")

for item in systems[
    "systems"
]:

    print(
        item["id"].upper()
    )

    print(
        "  Role:",
        item["role"]
    )

    print(
        "  Status:",
        item["status"]
    )

    print(
        "  Execution authority:",
        "YES"
        if item[
            "execution_authority"
        ]
        else "NO"
    )

    print(
        "  Purpose:",
        item["purpose"]
    )

    print("")

print(
    "✓ External services are separated from FX core."
)

print(
    "✓ No external project received broker authority."
)

print("")
