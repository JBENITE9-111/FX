from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.services.market_data.lse_global import LSEGlobalMarketData
from services.market_memory.research import historical_analogues
from services.market_memory.store import MarketMemoryStore
from services.market_memory.strategy_exam import examine_strategy


def main() -> int:
    parser = argparse.ArgumentParser(description="Build bounded, immutable FX historical research evidence.")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--asset-class", required=True)
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--limit", type=int, default=2000, choices=range(300, 5001), metavar="300..5000")
    parser.add_argument("--strategies", default="trend_following,macd_trend,breakout")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    rows = LSEGlobalMarketData().candles(
        args.symbol, args.timeframe, args.limit, args.dataset
    )
    store = MarketMemoryStore()
    ingested = store.ingest_bars(
        rows=rows, provider="London Strategic Edge",
        source_id="london-strategic-edge", dataset_name=args.dataset,
        symbol=args.symbol, asset_class=args.asset_class,
        timeframe=args.timeframe, adjustment_policy="PROVIDER_UNSPECIFIED",
    )
    artifact = ingested["manifest"]
    frame, _ = store.load_artifact(artifact["artifact_id"])
    analogues = (
        historical_analogues(frame, artifact_id=artifact["artifact_id"])
        if artifact["quality"]["status"] == "PASS"
        else {
            "available": False,
            "artifact_id": artifact["artifact_id"],
            "reason": "Historical analogues are blocked pending data-quality review.",
            "data_quality_status": artifact["quality"]["status"],
        }
    )
    exams = []
    for strategy_id in [value.strip() for value in args.strategies.split(",") if value.strip()]:
        exams.append(examine_strategy(
            store=store, artifact_id=artifact["artifact_id"], strategy_id=strategy_id
        ))
    print(json.dumps({
        "artifact": {key: artifact[key] for key in (
            "artifact_id", "dataset_id", "symbol", "asset_class", "timeframe",
            "coverage_start", "coverage_end", "rows", "quality", "raw_sha256",
            "curated_sha256",
        )},
        "analogues": analogues,
        "strategy_exams": exams,
        "paper_eligible": False,
        "live_trading": False,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
