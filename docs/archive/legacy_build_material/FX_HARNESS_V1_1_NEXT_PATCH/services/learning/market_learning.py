from __future__ import annotations

import asyncio
import math
import os
import time
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class MarketObservation:
    instrument: str
    ts: float
    bid: float | None
    ask: float | None
    last: float
    volume: float | None
    source: str
    venue: str | None


class OnlineMoments:
    """Welford online moments; cheap enough to update on every observation."""

    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, x: float):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.m2 += delta * delta2

    @property
    def variance(self) -> float:
        return self.m2 / (self.n - 1) if self.n > 1 else 0.0


class StreamingLearner:
    """Continuous *observation* learner.

    Safe meaning of "learn every second":
    - ingest real observations every second,
    - update online features/statistics,
    - persist predictions before outcomes,
    - update semantic memory after outcomes.

    It does NOT mutate/promote live models every second.
    """

    def __init__(self):
        self.interval = float(os.getenv("FX_MARKET_LEARNING_INTERVAL_SECONDS", "1"))
        self.retrain_interval = int(os.getenv("FX_MODEL_RETRAIN_INTERVAL_SECONDS", "3600"))
        self.last_price: dict[str, float] = {}
        self.returns = defaultdict(OnlineMoments)
        self.spreads = defaultdict(OnlineMoments)
        self._last_retrain_request = 0.0

    def observe(self, obs: MarketObservation) -> dict:
        prev = self.last_price.get(obs.instrument)
        ret = 0.0
        if prev and prev > 0 and obs.last > 0:
            ret = math.log(obs.last / prev)
            self.returns[obs.instrument].update(ret)
        self.last_price[obs.instrument] = obs.last

        spread_bps = None
        if obs.bid and obs.ask and obs.bid > 0 and obs.ask >= obs.bid:
            mid = (obs.bid + obs.ask) / 2
            spread_bps = (obs.ask - obs.bid) / mid * 10_000
            self.spreads[obs.instrument].update(spread_bps)

        return {
            "instrument": obs.instrument,
            "return_1": ret,
            "online_return_mean": self.returns[obs.instrument].mean,
            "online_return_variance": self.returns[obs.instrument].variance,
            "spread_bps": spread_bps,
            "online_spread_mean_bps": self.spreads[obs.instrument].mean,
        }

    def retrain_due(self) -> bool:
        now = time.time()
        if now - self._last_retrain_request >= self.retrain_interval:
            self._last_retrain_request = now
            return True
        return False

    async def run(self, fetch_observations, persist_observation, request_training):
        while True:
            started = time.time()
            observations = await fetch_observations()
            for obs in observations:
                features = self.observe(obs)
                await persist_observation(obs, features)

            if self.retrain_due():
                # Queue only. Training must run chronological OOS/WF/stress tests.
                # No model auto-promotion is allowed here.
                await request_training(reason="scheduled_streaming_refresh")

            elapsed = time.time() - started
            await asyncio.sleep(max(0.0, self.interval - elapsed))
