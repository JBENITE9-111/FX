from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    name: str

    def child(self, *parts: str) -> "Topic":
        suffix = ":".join(str(p).strip(":") for p in parts)
        return Topic(f"{self.name}:{suffix}" if suffix else self.name)


MARKET = Topic("market")
NEWS = Topic("news")
ECON = Topic("econ")
MACRO = Topic("macro")
CRYPTO = Topic("crypto")
DERIVATIVES = Topic("derivatives")
PORTFOLIO = Topic("portfolio")
PAPER = Topic("paper")
BROKER = Topic("broker")
AGENT = Topic("agent")
WORKFLOW = Topic("workflow")
RISK = Topic("risk")
BRAIN = Topic("brain")
SYSTEM = Topic("system")
