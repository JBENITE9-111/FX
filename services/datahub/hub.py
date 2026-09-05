from __future__ import annotations

import asyncio
import inspect
import time

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable


Subscriber = Callable[[str, Any], Any]
Producer = Callable[[str], Awaitable[Any] | Any]


@dataclass
class TopicPolicy:
    ttl_seconds: float = 5.0
    min_refresh_interval_seconds: float = 0.0
    push_only: bool = False


@dataclass
class TopicState:
    value: Any = None
    updated_at: float = 0.0
    last_fetch_started_at: float = 0.0
    fetching: bool = False
    subscribers: set[Subscriber] = field(default_factory=set)


class DataHub:
    """
    Local one-fetch / many-subscribers data plane.

    A provider fetch happens once per topic refresh.
    All charts/models/strategies/brain consumers can subscribe
    to the same normalized topic snapshot.
    """

    def __init__(self):
        self._states: dict[str, TopicState] = {}
        self._producers: dict[str, Producer] = {}
        self._policies: dict[str, TopicPolicy] = {}
        self._lock = asyncio.Lock()

    def register_producer(
        self,
        topic: str,
        producer: Producer,
        *,
        policy: TopicPolicy | None = None,
    ) -> None:
        self._producers[topic] = producer
        self._policies[topic] = policy or TopicPolicy()
        self._states.setdefault(topic, TopicState())

    def subscribe(
        self,
        topic: str,
        subscriber: Subscriber,
    ) -> Callable[[], None]:
        state = self._states.setdefault(topic, TopicState())
        state.subscribers.add(subscriber)

        def unsubscribe() -> None:
            state.subscribers.discard(subscriber)

        return unsubscribe

    async def publish(self, topic: str, value: Any) -> None:
        state = self._states.setdefault(topic, TopicState())
        state.value = value
        state.updated_at = time.time()

        for subscriber in list(state.subscribers):
            try:
                result = subscriber(topic, value)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                # One bad subscriber must not break the data plane.
                continue

    async def get(self, topic: str, *, force: bool = False) -> Any:
        state = self._states.setdefault(topic, TopicState())
        policy = self._policies.get(topic, TopicPolicy())
        now = time.time()

        if (
            not force
            and state.updated_at > 0
            and now - state.updated_at <= policy.ttl_seconds
        ):
            return state.value

        if policy.push_only:
            return state.value

        producer = self._producers.get(topic)
        if producer is None:
            return state.value

        async with self._lock:
            now = time.time()

            if (
                not force
                and state.updated_at > 0
                and now - state.updated_at <= policy.ttl_seconds
            ):
                return state.value

            min_wait = policy.min_refresh_interval_seconds

            if (
                state.last_fetch_started_at > 0
                and now - state.last_fetch_started_at < min_wait
                and state.value is not None
            ):
                return state.value

            state.fetching = True
            state.last_fetch_started_at = now

            try:
                result = producer(topic)

                if inspect.isawaitable(result):
                    result = await result

                await self.publish(topic, result)
                return result
            finally:
                state.fetching = False


datahub = DataHub()
