from __future__ import annotations

import asyncio
import os
import tempfile

import numpy as np

from services.cache.ttl_cache import SQLiteTTLCache
from services.datahub.hub import DataHub, TopicPolicy
from services.events.topics import MARKET
from services.execution.policy import (
    ExecutionPolicy,
    assert_safe_policy,
)
from services.monitoring.system_health import snapshot
from services.reconciliation.reconciler import reconcile_position_maps
from services.workflow.dag import WorkflowDAG, WorkflowNode


print("")
print("============================================================")
print(" FX COMPLETE FOUNDATION V2 TEST")
print("============================================================")
print("")

policy = ExecutionPolicy.from_env()
assert_safe_policy(policy)

assert policy.live_enabled is False
assert policy.ai_can_execute_live is False

print("✓ Execution policy")


health = snapshot(".")
assert health.status == "PASS"

print("✓ System health")


result = reconcile_position_maps(
    {"AAPL": 10},
    {"AAPL": 10},
)

assert result.status == "PASS"

blocked = reconcile_position_maps(
    {"AAPL": 10},
    {"AAPL": 9},
)

assert blocked.status == "BLOCK"
assert blocked.trading_allowed is False

print("✓ Reconciliation")


with tempfile.TemporaryDirectory() as tmp:
    cache = SQLiteTTLCache(
        f"{tmp}/cache.sqlite3"
    )

    cache.set(
        "market:AAPL",
        {"price": 100},
        ttl_seconds=60,
    )

    assert (
        cache.get("market:AAPL")["price"]
        == 100
    )

print("✓ TTL cache")


async def datahub_test():
    hub = DataHub()
    calls = {"count": 0}

    async def producer(topic):
        calls["count"] += 1
        return {
            "topic": topic,
            "price": 101.25,
        }

    topic = MARKET.child(
        "quote",
        "AAPL",
    ).name

    hub.register_producer(
        topic,
        producer,
        policy=TopicPolicy(
            ttl_seconds=60,
        ),
    )

    one = await hub.get(topic)
    two = await hub.get(topic)

    assert one == two
    assert calls["count"] == 1


asyncio.run(datahub_test())

print("✓ DataHub one-fetch/many-consumers")


async def dag_test():
    dag = WorkflowDAG()

    dag.add(
        WorkflowNode(
            "data",
            lambda ctx: {"quality": "PASS"},
        )
    )

    dag.add(
        WorkflowNode(
            "risk",
            lambda ctx: {
                "status": "PASS"
                if ctx["data"]["quality"] == "PASS"
                else "BLOCK"
            },
            depends_on=["data"],
        )
    )

    result = await dag.run()

    assert result["risk"]["status"] == "PASS"


asyncio.run(dag_test())

print("✓ Workflow DAG")

print("")
print("LIVE TRADING: DISABLED")
print("AI LIVE EXECUTION: DISABLED")
print("PAPER: ENABLED")
print("SHADOW: ENABLED")
print("")
print("============================================================")
print(" FX COMPLETE FOUNDATION V2: PASS")
print("============================================================")
print("")
