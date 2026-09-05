from __future__ import annotations

import threading

from typing import Any


class ServiceRegistry:
    def __init__(self):
        self._services: dict[str, Any] = {}
        self._lock = threading.RLock()

    def register(self, name: str, service: Any) -> None:
        with self._lock:
            if name in self._services:
                raise RuntimeError(
                    f"Service already registered: {name}"
                )
            self._services[name] = service

    def replace(self, name: str, service: Any) -> None:
        with self._lock:
            self._services[name] = service

    def get(self, name: str) -> Any:
        with self._lock:
            if name not in self._services:
                raise KeyError(name)
            return self._services[name]

    def list(self) -> list[str]:
        with self._lock:
            return sorted(self._services)


services = ServiceRegistry()
