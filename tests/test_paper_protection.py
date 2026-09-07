from __future__ import annotations

import json
import asyncio
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.local_paper import broker
from services.local_paper.protection import build_plan_options
from services.operations import store as operations_store
from backend.app.routes.fx_local_paper import PaperOrderRequest, order, protection_suggestions
from backend.app.routes.fx_local_paper_page import page as paper_page


class PaperProtectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.previous_db = broker.DB_PATH
        self.previous_operations_db = operations_store.DB_PATH
        broker.DB_PATH = Path(self.temporary.name) / "paper.sqlite3"
        operations_store.DB_PATH = Path(self.temporary.name) / "operations.sqlite3"

    def tearDown(self):
        broker.DB_PATH = self.previous_db
        operations_store.DB_PATH = self.previous_operations_db
        self.temporary.cleanup()

    def generated(self, plan_type="FIXED_1_5R", direction="BUY"):
        stop = 95.0 if direction == "BUY" else 105.0
        result = build_plan_options(
            instrument="TEST", asset_class="Stocks", direction=direction,
            entry=100.0, stop=stop, atr_14=2.0, notional=100.0,
            timeframe="1d", market_data_timestamp="2026-09-07T00:00:00Z",
            strategy_id="test-strategy", bot_id="test-bot",
            risk_capacity=broker.local_risk_capacity(),
        )
        selected = next(plan for plan in result["plans"] if plan["type"] == plan_type)
        return result, broker.create_protection_plan(selected)

    def open_position(self, plan):
        return broker.submit_market_order(
            instrument="TEST", asset_class="Stocks", side=plan["direction"],
            price=100.0, notional=100.0, strategy_id="test-strategy",
            bot_id="test-bot", stop=plan["structural_stop"],
            structural_invalidation=plan["structural_stop"],
            profit_plan=json.dumps({"type": plan["type"], "targets": plan["targets"]}),
            maximum_loss=plan["maximum_loss"], protection_plan_id=plan["plan_id"],
            protection_plan=plan, signal_id="open-test",
        )

    def test_risk_panel_calculation_is_explicit_and_conservative(self):
        result, _ = self.generated()
        risk = result["risk"]
        self.assertEqual("PASS", risk["decision"])
        self.assertAlmostEqual(1.0, risk["quantity"])
        self.assertAlmostEqual(5.0, risk["loss_at_stop"])
        self.assertGreater(risk["planned_loss_envelope"], risk["loss_at_stop"])
        self.assertAlmostEqual(250.0, risk["per_trade_risk_cap"])
        self.assertIn("larger loss", result["warning"])

    def test_generated_plan_rejects_mismatched_context(self):
        _, plan = self.generated()
        valid = broker.validate_protection_plan(
            plan["plan_id"], instrument="TEST", asset_class="Stocks",
            direction="BUY", entry=100, notional=100,
            strategy_id="test-strategy", bot_id="test-bot",
        )
        self.assertEqual(plan["plan_id"], valid["plan_id"])
        with self.assertRaisesRegex(ValueError, "does not match"):
            broker.validate_protection_plan(
                plan["plan_id"], instrument="AAPL", asset_class="Stocks",
                direction="BUY", entry=100, notional=100,
                strategy_id="test-strategy", bot_id="test-bot",
            )

    def test_generated_plan_rejects_expiry(self):
        _, plan = self.generated()
        with sqlite3.connect(broker.DB_PATH) as connection:
            connection.execute(
                "UPDATE protection_plans SET expires_at=0 WHERE plan_id=?",
                (plan["plan_id"],),
            )
        with self.assertRaisesRegex(ValueError, "expired"):
            broker.validate_protection_plan(
                plan["plan_id"], instrument="TEST", asset_class="Stocks",
                direction="BUY", entry=100, notional=100,
                strategy_id="test-strategy", bot_id="test-bot",
            )

    def test_each_generated_plan_record_has_a_unique_single_use_id(self):
        result, first = self.generated()
        fixed = next(plan for plan in result["plans"] if plan["type"] == "FIXED_1_5R")
        second = broker.create_protection_plan(fixed)
        self.assertNotEqual(first["plan_id"], second["plan_id"])

    def test_same_bar_stop_and_target_uses_stop_first(self):
        _, plan = self.generated()
        self.open_position(plan)
        events = broker.apply_protection_bar(
            "TEST", {"timestamp": "bar-1", "open": 100, "high": 108, "low": 94, "close": 102}
        )
        self.assertEqual("AUTO_STOP", events[0]["reason"])
        self.assertEqual([], broker.positions())

    def test_scale_plan_is_partial_idempotent_and_moves_stop(self):
        _, plan = self.generated("SCALE_1R_2R")
        self.open_position(plan)
        bar = {"timestamp": "bar-1", "open": 100, "high": 106, "low": 99, "close": 105}
        first = broker.apply_protection_bar("TEST", bar)
        self.assertEqual("AUTO_TARGET_1", first[0]["reason"])
        remaining = broker.positions()[0]
        self.assertAlmostEqual(0.5, remaining["quantity"])
        self.assertGreater(remaining["stop"], 100.0)
        self.assertTrue(json.loads(remaining["plan_state_json"])["target_1_filled"])
        self.assertEqual([], broker.apply_protection_bar("TEST", bar))

    def test_trailing_plan_activates_then_exits_on_later_bar(self):
        _, plan = self.generated("TRAIL_AFTER_1R")
        self.open_position(plan)
        activation = broker.apply_protection_bar(
            "TEST", {"timestamp": "bar-1", "open": 100, "high": 106, "low": 99, "close": 105}
        )
        self.assertEqual([], activation)
        armed = broker.positions()[0]
        self.assertTrue(json.loads(armed["plan_state_json"])["trail_active"])
        self.assertAlmostEqual(104.0, armed["stop"])
        exit_events = broker.apply_protection_bar(
            "TEST", {"timestamp": "bar-2", "open": 105, "high": 106, "low": 103, "close": 103.5}
        )
        self.assertEqual("AUTO_TRAIL", exit_events[0]["reason"])
        self.assertEqual([], broker.positions())

    def test_short_fixed_target_is_symmetric(self):
        _, plan = self.generated(direction="SELL")
        self.open_position(plan)
        events = broker.apply_protection_bar(
            "TEST", {"timestamp": "bar-1", "open": 100, "high": 101, "low": 92, "close": 93}
        )
        self.assertEqual("AUTO_TARGET_1", events[0]["reason"])
        self.assertEqual([], broker.positions())

    def test_gap_through_stop_uses_adverse_open_and_records_ledgers(self):
        _, plan = self.generated()
        self.open_position(plan)
        events = broker.apply_protection_bar(
            "TEST", {"timestamp": "bar-gap", "open": 90, "high": 92, "low": 89, "close": 91}
        )
        self.assertEqual("AUTO_STOP", events[0]["reason"])
        self.assertLess(events[0]["price"], 90.0)
        with sqlite3.connect(broker.DB_PATH) as connection:
            event_type = connection.execute(
                "SELECT event_type FROM training_events ORDER BY id DESC LIMIT 1"
            ).fetchone()[0]
            trade = connection.execute(
                "SELECT exit_reason,status FROM trades ORDER BY opened_at DESC LIMIT 1"
            ).fetchone()
        self.assertEqual("AUTO_STOP", event_type)
        self.assertEqual(("AUTO_STOP", "CLOSED"), trade)
        with sqlite3.connect(operations_store.DB_PATH) as connection:
            operation_type = connection.execute(
                "SELECT event_type FROM events ORDER BY occurred_at DESC LIMIT 1"
            ).fetchone()[0]
        self.assertEqual("paper.auto_stop", operation_type)

    def test_invalid_ohlc_bar_is_rejected(self):
        _, plan = self.generated()
        self.open_position(plan)
        with self.assertRaisesRegex(ValueError, "valid timestamped OHLC"):
            broker.apply_protection_bar(
                "TEST", {"timestamp": "bad", "open": 100, "high": 98, "low": 99, "close": 100}
            )

    def test_legacy_position_never_auto_executes_without_review(self):
        _, plan = self.generated()
        self.open_position(plan)
        with sqlite3.connect(broker.DB_PATH) as connection:
            connection.execute(
                "UPDATE positions SET legacy=1, protection_plan_json=NULL, last_evaluated_bar=NULL"
            )
        events = broker.apply_protection_bar(
            "TEST", {"timestamp": "legacy-bar", "open": 90, "high": 110, "low": 85, "close": 95}
        )
        self.assertEqual([], events)
        position = broker.positions()[0]
        self.assertEqual("AWAITING_REVIEW", json.loads(position["plan_state_json"])["status"])

    def test_user_defined_plan_waits_for_next_complete_bar(self):
        broker.submit_market_order(
            instrument="TEST", asset_class="Stocks", side="BUY", price=100,
            notional=100, strategy_id="manual", bot_id="manual", stop=95,
            structural_invalidation=95, profit_plan="Exit at 107.5",
            maximum_loss=5.1,
        )
        ambiguous_entry_bar = {"timestamp": "bar-1", "open": 100, "high": 101, "low": 94, "close": 100}
        self.assertEqual([], broker.apply_protection_bar("TEST", ambiguous_entry_bar))
        self.assertEqual(1, len(broker.positions()))
        next_bar = {"timestamp": "bar-2", "open": 96, "high": 97, "low": 94, "close": 95}
        self.assertEqual("AUTO_STOP", broker.apply_protection_bar("TEST", next_bar)[0]["reason"])

    def test_api_generated_plan_is_context_validated_and_consumed(self):
        rows = []
        for index in range(80):
            close = 100 + index * 0.1
            rows.append({
                "timestamp": f"2026-01-{(index % 28) + 1:02d}T00:00:00Z",
                "open": close - 0.1, "high": close + 1, "low": close - 1,
                "close": close,
            })

        class Provider:
            def candles(self, *_args):
                return rows

        with patch("backend.app.routes.fx_local_paper.LSEGlobalMarketData", return_value=Provider()):
            suggestion = asyncio.run(protection_suggestions(
                instrument="TEST", asset_class="Stocks", direction="BUY",
                notional=100, strategy_id="test-strategy", bot_id="test-bot",
            ))
        plan = suggestion["plans"][0]
        result = order(PaperOrderRequest(
            instrument="TEST", asset_class="Stocks", side="BUY",
            price=suggestion["entry"], notional=100,
            strategy_id="test-strategy", bot_id="test-bot",
            signal_id="api-protected-order-1",
            stop=suggestion["structural_stop"],
            structural_invalidation=suggestion["structural_stop"],
            profit_plan=plan["label"], maximum_loss=suggestion["maximum_loss"],
            protection_plan_id=plan["plan_id"], plan_source="FX_SUGGESTED",
        ))
        self.assertEqual("FILLED_LOCAL_PAPER", result["status"])
        self.assertEqual("CONSUMED", broker.get_protection_plan(plan["plan_id"])["status"])

        retry = order(PaperOrderRequest(
            instrument="TEST", asset_class="Stocks", side="BUY",
            price=suggestion["entry"], notional=100,
            strategy_id="test-strategy", bot_id="test-bot",
            signal_id=result["signal_id"], protection_plan_id=plan["plan_id"],
            plan_source="FX_SUGGESTED",
        ))
        self.assertEqual(result["order_id"], retry["order_id"])

    def test_page_clears_stale_context_and_formats_structured_errors(self):
        html = paper_page()
        self.assertIn("clearProtectionContext();loadLatestPaperPrice()", html)
        self.assertIn("formatApiError(result.detail", html)
        self.assertIn("Calculate BUY plan", html)
        self.assertNotIn("result.detail\n            ||", html)


if __name__ == "__main__":
    unittest.main()
