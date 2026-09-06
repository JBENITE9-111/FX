from __future__ import annotations

import asyncio

from backend.app.services.llm.router import FXLLMRouter
from services.chat import memory
from services.market_intelligence.yahoo_finance import _company_score, render_lookup


def test_personal_memory_recalls_relevant_older_messages(tmp_path, monkeypatch):
    monkeypatch.setattr(memory, "DB_PATH", tmp_path / "memory.sqlite3")
    memory.remember("personal", "user", "My preferred risk is half a percent per trade")
    memory.remember("personal", "assistant", "Stored locally")
    recalled = memory.recall("What is my preferred risk?", "personal")
    assert any("half a percent" in item["content"] for item in recalled)
    assert memory.status()["cloud_sync"] is False


def test_yahoo_company_matching_prefers_named_equity():
    equity = {"longname": "Space Exploration Technologies Corp.", "quoteType": "EQUITY"}
    token = {"longname": "SpaceX Tokenized Stock", "quoteType": "CRYPTOCURRENCY"}
    assert _company_score(equity, "SpaceX price") > _company_score(token, "SpaceX price")


def test_yahoo_renderer_never_invents_missing_price():
    text = render_lookup({"query": "unknown", "quote": None})
    assert "no verified public quote" in text
    assert "No price was invented" in text


def test_router_reconciles_only_responding_committee_members(monkeypatch):
    monkeypatch.setenv("OPENROUTER_COUNCIL_MODELS", "specialist/free")
    monkeypatch.setenv("GOOSE_CHAT_ENABLED", "true")
    router = FXLLMRouter()
    calls = []

    async def openrouter(model, messages, max_tokens=700):
        calls.append((model, messages[0]["content"]))
        return f"view from {model}"

    async def ollama(messages):
        calls.append(("ollama", messages[0]["content"]))
        return "local risk review"

    async def freellm(messages):
        raise RuntimeError("disabled")

    async def goose(question, evidence):
        calls.append(("goose", evidence))
        return "goose evidence review"

    monkeypatch.setattr(router, "_openrouter", openrouter)
    monkeypatch.setattr(router, "_ollama", ollama)
    monkeypatch.setattr(router, "_freellm", freellm)
    monkeypatch.setattr(router, "_goose", goose)
    result = asyncio.run(router.reason("Explain EUR/USD", {"verified": True}))
    assert result["provider"] == "FX Multi-Brain Committee"
    assert result["responding_brains"] == 4
    assert result["configured_brains"] == 4
    assert result["full_initial_participation"] is True
    assert {item["name"] for item in result["committee"]} == {
        "Kimi", "Ollama", "OpenRouter peer 1", "Goose"
    }
    assert result["deliberation_rounds"] == 2
    assert result["full_two_round_participation"] is True
    assert all(item["completed_rounds"] == 2 for item in result["committee"])
    assert result["answer"].startswith("FX PEER COMMITTEE")
    assert len(calls) == 8
    assert sum("round two" in prompt.lower() for _, prompt in calls) >= 3
