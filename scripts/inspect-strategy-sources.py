from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(
    "/Users/macmac/Documents/Codex/FX"
)

registry = json.loads(
    (
        ROOT
        / "strategy_sources"
        / "registry.json"
    ).read_text()
)

print("")
print("=" * 64)
print(" FX STRATEGY SOURCES")
print("=" * 64)
print("")

for source in registry[
    "sources"
]:

    location = (
        ROOT
        / source[
            "location"
        ]
    )

    exists = (
        location.exists()
    )

    print(
        source["name"]
    )

    print(
        "  Status:",
        source["status"]
    )

    print(
        "  Present:",
        "YES"
        if exists
        else "NO"
    )

    print(
        "  Broker authority:",
        "YES"
        if source[
            "broker_authority"
        ]
        else "NO"
    )

    print("")

print(
    "External strategies remain UNTRUSTED until FX validates them."
)

print("")
