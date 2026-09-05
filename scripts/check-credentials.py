import os

from dotenv import load_dotenv


load_dotenv()


checks = {
    "Ollama": (
        os.getenv(
            "OLLAMA_ENABLED",
            "true",
        ).lower()
        == "true"
    ),
    "OpenRouter": bool(
        os.getenv(
            "OPENROUTER_API_KEY"
        )
    ),
    "Kimi": bool(
        os.getenv(
            "KIMI_API_KEY"
        )
    ),
    "Hugging Face": bool(
        os.getenv(
            "HF_TOKEN"
        )
    ),
    "Alpaca Paper": bool(
        os.getenv(
            "ALPACA_PAPER_KEY"
        )
        and os.getenv(
            "ALPACA_PAPER_SECRET"
        )
    ),
    "Binance Testnet": bool(
        os.getenv(
            "BINANCE_TESTNET_API_KEY"
        )
        and os.getenv(
            "BINANCE_TESTNET_API_SECRET"
        )
    ),
}


print("")
print("FX CREDENTIAL STATUS")
print("=" * 48)

for name, configured in checks.items():
    state = (
        "✓ configured"
        if configured
        else "○ not configured"
    )

    print(
        f"{name:<24} {state}"
    )

print("")
print(
    "LIVE TRADING ENABLED:",
    os.getenv(
        "LIVE_TRADING_ENABLED",
        "false",
    ),
)

print("")
