import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from backend.app.services.llm.router import FXLLMRouter


load_dotenv(ROOT / ".env")


async def main():
    llm = FXLLMRouter()

    result = await llm.reason(
        """
Tell me, in very simple plain English, that the FX local AI brain
is working.

Use no technical jargon.

Do not give investment advice.
"""
    )

    print("")
    print("FX LOCAL AI TEST")
    print("=" * 50)
    print("")
    print("AI provider:", result.get("provider"))
    print("AI model:", result.get("model"))
    print("")
    print(result.get("answer"))
    print("")


asyncio.run(main())
