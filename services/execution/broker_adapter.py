from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CanonicalOrder:
    client_order_id: str
    instrument_id: str
    side: str
    quantity: float
    order_type: str
    limit_price: float | None = None
    stop_price: float | None = None
    reduce_only: bool = False


@dataclass(frozen=True)
class CanonicalOrderResult:
    broker_order_id: str
    client_order_id: str
    status: str
    raw_status: str | None = None


class BrokerAdapter(ABC):
    """
    External broker schemas terminate at this boundary.

    The rest of FX should operate on canonical FX types.
    """

    broker_id: str

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def account(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def positions(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def open_orders(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def submit_order(
        self,
        order: CanonicalOrder,
    ) -> CanonicalOrderResult:
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(
        self,
        broker_order_id: str,
    ) -> CanonicalOrderResult:
        raise NotImplementedError
