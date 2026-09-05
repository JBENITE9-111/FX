from __future__ import annotations

import asyncio

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


NodeFn = Callable[
    [dict[str, Any]],
    Awaitable[dict[str, Any]] | dict[str, Any],
]


@dataclass
class WorkflowNode:
    node_id: str
    fn: NodeFn
    depends_on: list[str] = field(default_factory=list)


class WorkflowDAG:
    """
    Small typed DAG foundation for FX Brain workflows.
    """

    def __init__(self):
        self.nodes: dict[str, WorkflowNode] = {}

    def add(self, node: WorkflowNode) -> None:
        if node.node_id in self.nodes:
            raise RuntimeError(
                f"Duplicate workflow node: {node.node_id}"
            )

        self.nodes[node.node_id] = node

    def _validate(self) -> None:
        for node in self.nodes.values():
            for dep in node.depends_on:
                if dep not in self.nodes:
                    raise RuntimeError(
                        f"{node.node_id} depends on missing node {dep}"
                    )

    async def run(
        self,
        initial_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate()

        context = dict(initial_context or {})
        completed: set[str] = set()
        results: dict[str, Any] = {}

        while len(completed) < len(self.nodes):
            ready = [
                node
                for node in self.nodes.values()
                if node.node_id not in completed
                and all(dep in completed for dep in node.depends_on)
            ]

            if not ready:
                raise RuntimeError(
                    "Workflow cycle detected or dependencies unresolved."
                )

            for node in ready:
                value = node.fn(context)

                if asyncio.iscoroutine(value):
                    value = await value

                results[node.node_id] = value
                context[node.node_id] = value
                completed.add(node.node_id)

        return results
