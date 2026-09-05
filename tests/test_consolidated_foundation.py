import tempfile
import time
import unittest
from pathlib import Path

from services.campaigns.store import CampaignStore
from services.local_paper import broker
from services.operations import store as operations_store
from services.learning.status import learning_overview
from services.instruments.training_universe import search_training_catalog
from backend.app.services.bots.runtime import bots
from backend.app.services.research.grounded_answer import (
    grounded_context_answer,
    identify_symbols,
    operational_answer,
)


class ConsolidatedFoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous_db = broker.DB_PATH
        self.previous_operations_db = operations_store.DB_PATH
        broker.DB_PATH = Path(self.temp.name) / "paper.sqlite3"
        operations_store.DB_PATH = Path(self.temp.name) / "operations.sqlite3"

    def tearDown(self):
        broker.DB_PATH = self.previous_db
        operations_store.DB_PATH = self.previous_operations_db
        self.temp.cleanup()

    def protected_order(self, **changes):
        values = dict(
            instrument="XAUUSD", asset_class="Commodities", side="BUY",
            price=100, quantity=1, strategy_id="gold-trend", bot_id="gold-1",
            signal_id="signal-1", stop=95, structural_invalidation=95,
            profit_plan="FIXED_TARGET_110", maximum_loss=5,
        )
        values.update(changes)
        return broker.submit_market_order(**values)

    def test_new_position_requires_protection(self):
        with self.assertRaises(ValueError):
            broker.submit_market_order(
                instrument="XAUUSD", asset_class="Commodities", side="BUY",
                price=100, quantity=1, strategy_id="s", bot_id="b",
            )

    def test_legacy_positions_receive_explicit_protection(self):
        now = time.time()
        with broker._connect() as conn:
            conn.execute(
                """INSERT INTO positions(
                    position_id,instrument,asset_class,strategy_id,bot_id,side,
                    quantity,average_price,last_price,realized_pnl,created_at,updated_at,legacy
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                ("legacy-1", "AAPL", "Stocks", "legacy", "legacy-bot", 1,
                 2.0, 100.0, 90.0, 0.0, now, now, 1),
            )
        self.assertEqual(broker.protect_legacy_positions(), 1)
        position = broker.positions()[0]
        self.assertAlmostEqual(position["stop"], 88.2)
        self.assertAlmostEqual(position["maximum_loss"], 3.6)
        self.assertIn("MIGRATED_SCALE_1R_2R", position["profit_plan"])

    def test_position_size_cannot_exceed_declared_maximum_loss(self):
        with self.assertRaisesRegex(ValueError, "maximum loss"):
            self.protected_order(quantity=2, maximum_loss=5)

    def test_long_short_accounting_and_idempotency(self):
        first = self.protected_order()
        duplicate = self.protected_order()
        self.assertEqual(first.order_id, duplicate.order_id)
        self.assertAlmostEqual(broker.get_account()["equity"], 100000)
        broker.close_position(broker.positions()[0]["position_id"], 110)
        self.assertAlmostEqual(broker.get_account()["cash"], 100010)
        self.protected_order(
            instrument="EURUSD", asset_class="Forex", side="SHORT",
            bot_id="fx-1", strategy_id="fx-trend", signal_id="signal-2",
            stop=105, structural_invalidation=105, profit_plan="FIXED_TARGET_90",
        )
        broker.close_position(broker.positions()[0]["position_id"], 90)
        self.assertAlmostEqual(broker.get_account()["cash"], 100020)

    def test_campaign_is_created_waiting_for_readiness_workflow(self):
        store = CampaignStore(Path(self.temp.name) / "campaigns.sqlite3")
        result = store.create(
            bot_id="gold-1", strategy_id="gold-trend", strategy_version="1",
            instrument="XAUUSD", asset_class="Commodities", capital=100,
            target_type="PROFIT_DOLLARS", target_value=20, maximum_loss=10,
            deadline=time.time() + 3600,
        )
        self.assertEqual(result["status"], "DRAFT")

    def test_learning_never_claims_current_failed_runs_are_eligible(self):
        result = learning_overview()
        self.assertEqual(result["summary"]["paper_eligible"], 0)
        self.assertTrue(all(not row["eligible"] for row in result["records"]))
        self.assertTrue(all(row["stage"] != "REJECTED" for row in result["records"]))

    def test_market_price_chat_has_verified_non_llm_fallback(self):
        answer = grounded_context_answer(
            "What is the gold price right now?",
            {"symbol": "XAU/USD", "model_council": {}},
            [{"timestamp": "2026-09-04T20:00:00Z", "close": 4429.19}],
        )
        self.assertIn("4429.19", answer)
        self.assertIn("London Strategic Edge", answer)

    def test_global_training_catalog_is_not_limited_to_seed_instruments(self):
        stocks = search_training_catalog(asset_class="Stocks", query="Microsoft")
        forex = search_training_catalog(asset_class="Forex", limit=500)
        self.assertTrue(any(row["symbol"] == "MSFT" for row in stocks["instruments"]))
        self.assertGreater(stocks["catalog_total"], 4_000)
        self.assertGreaterEqual(forex["matched"], 50)

    def test_chat_resolves_named_market_and_answers_system_questions_locally(self):
        self.assertEqual(identify_symbols("What is the gold price? ")[0], "XAU/USD")
        answer = operational_answer("What are the running bots doing?")
        self.assertIn("local", answer.lower())
        self.assertIn("do not place orders", answer.lower())

    def test_watch_only_bot_teams_cover_every_supported_market_group(self):
        rows = bots.list()
        ids = {row["id"] for row in rows}
        self.assertTrue({"global_equity", "forex", "crypto", "commodities", "indices", "etfs", "futures"} <= ids)
        self.assertTrue(all(not row["can_place_orders"] for row in rows))
        self.assertTrue(all(not row["learns_while_scanning"] for row in rows))


if __name__ == "__main__":
    unittest.main()
