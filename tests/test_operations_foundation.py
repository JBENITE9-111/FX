import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from services.events.contracts import SignalState, StandardSignal
from services.operations import store
from services.operations.notifications import channel_health, route_event
from services.operations.reports import generate_report, render_markdown


class OperationsFoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = store.DB_PATH
        store.DB_PATH = Path(self.temp.name) / "operations.sqlite3"
        store.initialize()

    def tearDown(self):
        store.DB_PATH = self.previous
        self.temp.cleanup()

    def favorite(self):
        return store.save_favorite({
            "instrument_id": "lse:test:AAPL", "symbol": "AAPL", "name": "Apple",
            "asset_class": "Stocks", "provider": "London Strategic Edge",
            "execution_timeframe": "1d", "context_timeframes": ["1w"],
            "strategy_id": "trend_following", "bot_id": "trading_team",
            "channels": ["app"],
        })

    def test_favorite_persists_and_is_unique(self):
        first = self.favorite()
        second = self.favorite()
        self.assertEqual(first["favorite_id"], second["favorite_id"])
        self.assertEqual(len(store.list_favorites()), 1)
        analyzed = store.save_favorite({**second, "last_analysis_at": 123.0})
        self.assertEqual(analyzed["last_analysis_at"], 123.0)

    def test_schedule_persists_after_store_reinitialization(self):
        favorite = self.favorite()
        saved = store.save_schedule({"favorite_id": favorite["favorite_id"], "interval_minutes": 5})
        store.initialize()
        self.assertEqual(store.get_schedule(saved["schedule_id"])["interval_minutes"], 5)

    def test_event_and_delivery_deduplicate(self):
        event1 = store.record_event(event_type="signal.state_changed", source="test", subject_type="favorite",
                                    subject_id="one", state="WATCHING", payload={}, dedup_key="one:watching")
        event2 = store.record_event(event_type="signal.state_changed", source="test", subject_type="favorite",
                                    subject_id="one", state="WATCHING", payload={}, dedup_key="one:watching")
        self.assertEqual(event1["event_id"], event2["event_id"])
        route_event(event1, channels=["app", "app"], message="Watching")
        deliveries = store.list_deliveries()
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0]["status"], "SENT")

    def test_unconfigured_external_channels_are_truthful(self):
        health = channel_health()
        self.assertIn(health["telegram"]["status"], {"NOT_CONFIGURED", "CONFIGURED"})
        self.assertIn(health["discord"]["status"], {"NOT_CONFIGURED", "CONFIGURED"})

    def test_bot_report_records_missing_evidence_and_exports_markdown(self):
        report = generate_report("bot", "global_scanner")
        self.assertTrue(report["body"]["missing_data"])
        self.assertIn("Research and local paper trading only", render_markdown(report))

    def test_actionable_signal_cannot_bypass_protection_or_risk(self):
        with self.assertRaises(ValidationError):
            StandardSignal(
                instrument_id="lse:test:AAPL", symbol="AAPL", asset_class="Stocks",
                market_data_asof=datetime.now(timezone.utc), provider="London Strategic Edge",
                strategy_id="trend", strategy_version="1", bot_id="bot", execution_timeframe="1d",
                state=SignalState.LONG_CONFIRMED, direction="LONG", entry=100,
                supervisor_decision="APPROVE_FOR_PAPER", risk_decision="BLOCK",
                eligibility="PAPER_ELIGIBLE",
            )

    def test_research_signal_may_preserve_unknown_fields(self):
        signal = StandardSignal(
            instrument_id="lse:test:AAPL", symbol="AAPL", asset_class="Stocks",
            market_data_asof=datetime.now(timezone.utc), provider="London Strategic Edge",
            strategy_id="trend", strategy_version="1", bot_id="bot", execution_timeframe="1d",
            state=SignalState.WATCHING, direction="NO_TRADE",
            supervisor_decision="INSUFFICIENT_DATA", risk_decision="BLOCK",
        )
        self.assertIsNone(signal.calibrated_confidence)
        self.assertEqual(signal.confidence_label, "UNVERIFIED_SCORE")


if __name__ == "__main__":
    unittest.main()
