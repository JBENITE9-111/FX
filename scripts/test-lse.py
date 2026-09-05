import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

key = os.getenv("LSE_API_KEY", "").strip()

print("")
print("LONDON STRATEGIC EDGE")
print("=" * 52)
print("")

if not key:
    print("London Strategic Edge has not been connected yet.")
    print("")
    print("Your API key is missing from the private FX settings.")
    print("")
    sys.exit(1)

print("✓ Your London Strategic Edge key was found.")
print("✓ The key will not be printed.")
print("")

try:
    from lse import LSE

    client = LSE(api_key=key)

    print("Checking the LSE market catalog...")

    stocks = client.catalog("stocks")

    print("✓ FX reached the London Strategic Edge market catalog.")
    print("✓ Stock instruments available:", len(stocks))
    print("")

    print("Checking Apple historical market data...")

    apple = client.candles(
        "AAPL",
        "1d",
        limit=5,
        order="desc",
    )

    if apple:
        print("✓ Apple historical data is working.")
        print("✓ Recent Apple candles received:", len(apple))
    else:
        print("⚠ LSE connected, but Apple returned no recent candles.")

    print("")
    print("Checking Gold / XAU/USD...")

    gold = client.candles(
        "XAU/USD",
        "1h",
        limit=5,
        order="desc",
    )

    if gold:
        print("✓ Gold data is working.")
        print("✓ Recent XAU/USD candles received:", len(gold))

        latest = gold[0]

        print("")
        print("Most recent gold information received:")
        print("")

        for field in [
            "timestamp",
            "ts",
            "time",
            "open",
            "high",
            "low",
            "close",
        ]:
            if field in latest:
                print(
                    field.replace("_", " ").title()
                    + ":",
                    latest[field],
                )

    else:
        print("⚠ LSE connected, but Gold returned no recent candles.")

    print("")
    print("============================================================")
    print(" LONDON STRATEGIC EDGE IS CONNECTED")
    print("============================================================")
    print("")
    print("FX can now begin using LSE for real research data.")
    print("")
    print("No real-money trade was sent.")
    print("Paper Trading remains active.")
    print("")

except Exception as exc:

    print("")
    print("FX could not complete the London Strategic Edge test.")
    print("")
    print("Your Alpaca account and money are not affected.")
    print("")
    print("Technical information:")
    print(str(exc))
    print("")
    sys.exit(1)
