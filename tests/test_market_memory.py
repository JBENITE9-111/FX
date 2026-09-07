from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from services.market_memory.quality import (
    HistoricalDataQualityError,
    normalize_and_validate_bars,
)
from services.market_memory.research import historical_analogues
from services.market_memory.store import MarketMemoryStore
from services.market_memory.strategy_exam import examine_strategy


def golden_bars(count: int = 500) -> list[dict]:
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    rows = []
    price = 100.0
    for index in range(count):
        drift = 0.001 if (index // 80) % 2 == 0 else -0.0007
        shock = ((index % 13) - 6) * 0.00015
        opened = price
        closed = price * (1 + drift + shock)
        rows.append({
            "timestamp": (start + timedelta(days=index)).isoformat(),
            "open": opened,
            "high": max(opened, closed) * 1.002,
            "low": min(opened, closed) * 0.998,
            "close": closed,
            "volume": 1000 + index,
            "symbol": "GOLDEN",
        })
        price = closed
    return rows


class MarketMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temporary.name)
        self.store = MarketMemoryStore(
            root=self.project_root / "data" / "historical",
            project_root=self.project_root,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def ingest(self):
        return self.store.ingest_bars(
            rows=golden_bars(), provider="London Strategic Edge",
            source_id="london-strategic-edge", dataset_name="golden",
            symbol="GOLDEN", asset_class="Test", timeframe="1d",
            adjustment_policy="TEST_UNADJUSTED",
        )

    def test_quality_rejects_duplicate_timestamp(self):
        rows = golden_bars(10)
        rows.append(dict(rows[-1]))
        with self.assertRaisesRegex(HistoricalDataQualityError, "duplicate"):
            normalize_and_validate_bars(rows)

    def test_quality_flags_suspicious_discontinuity_for_review(self):
        rows = golden_bars(10)
        rows[-1]["open"] *= 2
        rows[-1]["high"] *= 2
        rows[-1]["low"] *= 2
        rows[-1]["close"] *= 2
        _, report = normalize_and_validate_bars(rows)
        self.assertEqual("REVIEW_REQUIRED", report["status"])
        self.assertEqual(1, report["suspicious_return_rows"])

    def test_content_addressed_ingest_is_immutable_and_deduplicated(self):
        first = self.ingest()
        second = self.ingest()
        self.assertFalse(first["deduplicated"])
        self.assertTrue(second["deduplicated"])
        self.assertEqual(
            first["manifest"]["artifact_id"], second["manifest"]["artifact_id"]
        )
        frame, manifest = self.store.load_artifact(first["manifest"]["artifact_id"])
        self.assertEqual(500, len(frame))
        self.assertEqual("PASS", manifest["quality"]["status"])
        self.assertEqual("UTC", manifest["quality"]["timezone"])

    def test_analogues_are_dated_non_overlapping_and_expose_downside(self):
        artifact = self.ingest()["manifest"]
        frame, _ = self.store.load_artifact(artifact["artifact_id"])
        result = historical_analogues(
            frame, artifact_id=artifact["artifact_id"],
            forward_periods=5, top_k=8, exclusion_periods=20,
        )
        self.assertTrue(result["available"])
        self.assertEqual(8, result["sample_size"])
        self.assertIsNotNone(result["worst_forward_return"])
        current = datetime.fromisoformat(result["current_timestamp"])
        for match in result["matches"]:
            observed = datetime.fromisoformat(match["timestamp"])
            self.assertLessEqual(observed, current - timedelta(days=25))

    def test_strategy_exam_is_chronological_cost_stressed_and_never_eligible(self):
        artifact = self.ingest()["manifest"]
        result = examine_strategy(
            store=self.store, artifact_id=artifact["artifact_id"],
            strategy_id="trend_following",
        )
        self.assertEqual("RESEARCH_ONLY", result["status"])
        self.assertEqual("NOT_ELIGIBLE", result["eligibility"])
        self.assertEqual(
            {"development", "validation", "locked_test"},
            set(result["cost_stress"]["10.0"]),
        )
        self.assertGreater(
            result["cost_stress"]["5.0"]["locked_test"]["total_return"],
            result["cost_stress"]["20.0"]["locked_test"]["total_return"],
        )
        metrics = result["cost_stress"]["10.0"]["locked_test"]
        for key in (
            "cagr", "calmar", "annualized_volatility", "tail_loss_5pct",
            "expectancy_per_active_bar", "payoff_ratio", "turnover",
        ):
            self.assertIn(key, metrics)
        repeated = examine_strategy(
            store=self.store, artifact_id=artifact["artifact_id"],
            strategy_id="trend_following",
        )
        self.assertEqual(result["experiment_id"], repeated["experiment_id"])


if __name__ == "__main__":
    unittest.main()
