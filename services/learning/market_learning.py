from __future__ import annotations

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
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, value: float) -> None:
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        delta2 = value - self.mean
        self.m2 += delta * delta2

    @property
    def variance(self) -> float:
        if self.n <= 1:
            return 0.0
        return self.m2 / (self.n - 1)

class StreamingLearner:
    def __init__(self):
        self.last_price = {}
        self.returns = defaultdict(OnlineMoments)
        self.interval = float(
            os.getenv("FX_MARKET_LEARNING_INTERVAL_SECONDS", "1")
        )
        self.retrain_interval = int(
            os.getenv("FX_MODEL_RETRAIN_INTERVAL_SECONDS", "3600")
        )
        self._last_retrain_request = 0.0

    def observe(self, observation: MarketObservation) -> dict:
        previous = self.last_price.get(observation.instrument)
        ret = 0.0

        if previous is not None and previous > 0 and observation.last > 0:
            ret = math.log(observation.last / previous)
            self.returns[observation.instrument].update(ret)

        self.last_price[observation.instrument] = observation.last

        return {
            "instrument": observation.instrument,
            "return_1": ret,
            "mean": self.returns[observation.instrument].mean,
            "variance": self.returns[observation.instrument].variance,
        }

    def retrain_due(self) -> bool:
        now = time.time()
        if now - self._last_retrain_request >= self.retrain_interval:
            self._last_retrain_request = now
            return True
        return False
