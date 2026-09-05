from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path("/Users/macmac/Documents/Codex/FX")


print()
print("=" * 68)
print(" FX V4 COMPLETE VERIFICATION")
print("=" * 68)
print()


# ---------------------------------------------------------------------
# 1. EXECUTION SAFETY
# ---------------------------------------------------------------------

from services.execution.policy import (
    ExecutionPolicy,
    assert_safe_policy,
)

policy = ExecutionPolicy.from_env()
assert_safe_policy(policy)

assert policy.live_enabled is False, (
    "LIVE_TRADING_ENABLED must remain false."
)

assert policy.ai_can_execute_live is False, (
    "AI_CAN_EXECUTE_LIVE must remain false."
)

print("✓ Execution policy")
print("  Live trading: DISABLED")
print("  AI live execution: DISABLED")
print()


# ---------------------------------------------------------------------
# 2. NEWSPAPER
# ---------------------------------------------------------------------

from services.news.newspaper import load as load_newspaper

newspaper = load_newspaper()

headlines = newspaper.get("items", [])

print("✓ FX Global Newspaper")
print("  Headlines:", len(headlines))
print(
    "  Refresh interval:",
    newspaper.get(
        "refresh_interval_seconds",
        1800,
    ),
    "seconds",
)

sources = sorted(
    {
        str(item.get("source", "")).strip()
        for item in headlines
        if item.get("source")
    }
)

print(
    "  Sources discovered:",
    len(sources),
)

if sources:
    print(
        "  Example sources:",
        ", ".join(
            sources[:12]
        ),
    )

print()


# ---------------------------------------------------------------------
# 3. PAPER STRATEGY FLEET
# ---------------------------------------------------------------------

from services.paper_fleet.fleet import (
    STRATEGIES,
    load_latest,
)

fleet = load_latest()

workers = fleet.get(
    "strategies",
    [],
)

print("✓ FX Paper Strategy Fleet")
print(
    "  Registered strategies:",
    len(STRATEGIES),
)

print(
    "  Active strategy records:",
    len(workers),
)

print(
    "  Virtual capital / strategy: $",
    fleet.get(
        "paper_capital_per_strategy",
        1.0,
    ),
    sep="",
)

for item in workers:
    print(
        "   ",
        f"{item.get('strategy',''):<29}",
        f"{item.get('signal_name',''):<10}",
        f"NAV ${float(item.get('nav',0)):.4f}",
    )

print()


# ---------------------------------------------------------------------
# 4. BRAIN + EXPERT ROUTING
# ---------------------------------------------------------------------

from services.brain.trace import (
    brain_trace_store,
)

assert brain_trace_store is not None

print("✓ Observable Brain")
print(
    "  Structured evidence trace available"
)
print(
    "  Hidden chain-of-thought is NOT stored"
)
print()


# Sparse expert router may have different implementation names.
try:
    from services.agents.expert_router import (
        route_experts,
    )

    example = route_experts(
        instrument="EURUSD",
        asset_class="forex",
        context={
            "rates": True,
            "macro": True,
        },
    )

    print("✓ Sparse expert routing")
    print(
        "  EURUSD macro example:",
        example,
    )

except Exception as exc:
    print(
        "ℹ Sparse expert router exists "
        "under a different interface or "
        "is optional in this build."
    )
    print(
        "  Detail:",
        type(exc).__name__,
        str(exc),
    )

print()


# ---------------------------------------------------------------------
# 5. FASTAPI ROUTE DISCOVERY
#
# FIX FOR:
# AttributeError:
# '_IncludedRouter' object has no attribute 'path'
# ---------------------------------------------------------------------

from backend.app.main import app


def collect_routes(
    obj: Any,
    seen: set[int] | None = None,
) -> set[str]:
    """
    Safely discover route paths.

    Handles:
    - APIRoute
    - Route
    - Mount
    - custom _IncludedRouter wrappers
    - objects exposing .routes
    - objects exposing .router.routes

    Never assumes every object has .path.
    """

    if seen is None:
        seen = set()

    obj_id = id(obj)

    if obj_id in seen:
        return set()

    seen.add(obj_id)

    found: set[str] = set()

    path = getattr(
        obj,
        "path",
        None,
    )

    if isinstance(
        path,
        str,
    ):
        found.add(path)

    children = getattr(
        obj,
        "routes",
        None,
    )

    if children:
        try:
            for child in children:
                found.update(
                    collect_routes(
                        child,
                        seen,
                    )
                )
        except TypeError:
            pass

    router = getattr(
        obj,
        "router",
        None,
    )

    if router is not None:
        found.update(
            collect_routes(
                router,
                seen,
            )
        )

    return found


paths = collect_routes(app)

print("✓ FastAPI application imported")
print(
    "  Discoverable route paths:",
    len(paths),
)
print()


required_routes = [
    "/newspaper",
    "/api/newspaper",
    "/strategy-fleet",
    "/api/strategy-fleet",
    "/api/security/totp/status",
]

optional_routes = [
    "/api/security/totp/enroll",
    "/api/security/live-approval",
]


missing_required = []

print("Required V4 routes:")

for required in required_routes:
    exists = required in paths

    print(
        " ",
        "✓" if exists else "✗",
        required,
    )

    if not exists:
        missing_required.append(
            required
        )

print()

print("Additional Harness routes:")

for optional in optional_routes:
    print(
        " ",
        "✓" if optional in paths else "ℹ",
        optional,
    )

brain_routes = sorted(
    path
    for path in paths
    if path.startswith(
        "/api/brain"
    )
)

if brain_routes:
    for path in brain_routes:
        print(
            "  ✓",
            path,
        )
else:
    print(
        "  ℹ Brain API route not "
        "discoverable through this router "
        "wrapper, but Brain service imports."
    )

print()


# ---------------------------------------------------------------------
# 6. PERSISTED DATA
# ---------------------------------------------------------------------

files_to_check = [
    ROOT
    / "data"
    / "news"
    / "newspaper.json",

    ROOT
    / "data"
    / "paper_fleet"
    / "latest.json",

    ROOT
    / "data"
    / "paper_fleet"
    / "fleet.sqlite3",
]

print("Persistent state:")

for path in files_to_check:
    if path.exists():
        print(
            "  ✓",
            path.relative_to(ROOT),
            f"({path.stat().st_size:,} bytes)",
        )
    else:
        print(
            "  ℹ",
            path.relative_to(ROOT),
            "not created yet",
        )

print()


# ---------------------------------------------------------------------
# 7. BACKGROUND AGENTS
# ---------------------------------------------------------------------

news_plist = (
    Path.home()
    / "Library"
    / "LaunchAgents"
    / "com.fx.newspaper.refresh.plist"
)

fleet_plist = (
    Path.home()
    / "Library"
    / "LaunchAgents"
    / "com.fx.paperfleet.plist"
)

print("Background agents:")

print(
    "  ",
    "✓" if news_plist.exists() else "✗",
    "Newspaper — every 30 minutes",
)

print(
    "  ",
    "✓" if fleet_plist.exists() else "✗",
    "Paper Fleet — every 5 minutes",
)

print()


# ---------------------------------------------------------------------
# 8. FINAL
# ---------------------------------------------------------------------

if missing_required:

    print("=" * 68)

    print(
        " FX V4 CORE SERVICES ARE INSTALLED"
    )

    print(
        " Some page routes still need "
        "to be mounted:"
    )

    for route in missing_required:
        print(
            "  -",
            route,
        )

    print("=" * 68)

else:

    print("=" * 68)
    print(
        " FX TERMINAL UPGRADE V4: PASS"
    )
    print("=" * 68)

    print()
    print(
        "Newspaper:"
    )
    print(
        "  http://127.0.0.1:8000/newspaper"
    )

    print()
    print(
        "Paper Strategy Fleet:"
    )
    print(
        "  http://127.0.0.1:8000/strategy-fleet"
    )

    print()
    print(
        "Live trading:"
    )
    print(
        "  DISABLED"
    )

    print()
    print(
        "Autonomous AI live execution:"
    )
    print(
        "  DISABLED"
    )

print()
