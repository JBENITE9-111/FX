import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from backend.app.services.brokers.alpaca_paper import (
    AlpacaPaperBroker,
)


load_dotenv(ROOT / ".env")


broker = AlpacaPaperBroker()

account = broker.account()

print("")
print("ALPACA PAPER ACCOUNT")
print("=" * 50)
print("")
print("Your connection is working.")
print("")
print("This is a PAPER trading account.")
print("No real money is being used.")
print("")
print("Paper cash available:")
print(account.cash)
print("")
print("Paper account value:")
print(account.equity)
print("")
print("Paper buying power:")
print(account.buying_power)
print("")
print("✓ Alpaca Paper is connected")
print("✓ Real-money trading is still disabled")
print("")
