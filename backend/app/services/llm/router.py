import asyncio
import os
from typing import Any

import httpx

from openai import (
    AsyncOpenAI,
)


class FXLLMRouter:

    def __init__(self):

        self.openrouter_key = (
            os.getenv(
                "OPENROUTER_API_KEY",
                "",
            )
            .strip()
        )

        self.openrouter_model = (
            os.getenv(
                "OPENROUTER_MODEL",
                "moonshotai/kimi-k2.6:free",
            )
            .strip()
        )

        self.ollama_url = (
            os.getenv(
                "OLLAMA_BASE_URL",
                "http://127.0.0.1:11434",
            )
        )

        self.ollama_model = (
            os.getenv(
                "OLLAMA_MODEL",
                "qwen3:1.7b",
            )
        )

    async def _kimi(
        self,
        messages,
        max_tokens=900,
    ):

        if not self.openrouter_key:

            raise RuntimeError(
                "Kimi is not configured."
            )

        client = AsyncOpenAI(
            api_key=(
                self.openrouter_key
            ),
            base_url=(
                "https://openrouter.ai/api/v1"
            ),
        )

        response = (
            await client
            .chat.completions
            .create(
                model=(
                    self.openrouter_model
                ),
                messages=messages,
                temperature=0.15,
                max_tokens=max_tokens,
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
            or ""
        )

    async def _ollama(
        self,
        messages,
    ):

        timeout = httpx.Timeout(
            connect=5,
            read=45,
            write=20,
            pool=20,
        )

        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:

            response = await client.post(
                self.ollama_url
                + "/api/chat",

                json={
                    "model":
                        self.ollama_model,

                    "messages":
                        messages,

                    "stream":
                        False,

                    "think":
                        False,

                    "keep_alive":
                        "30m",

                    "options":{
                        "temperature":
                            0.1,

                        "num_predict":
                            400,
                    },
                },
            )

            response.raise_for_status()

            return (
                response.json()
                ["message"]
                ["content"]
            )

    async def reason(
        self,
        question: str,
        context: dict[str, Any]
        | None = None,
    ):

        evidence = (
            str(context)
            if context
            else (
                "No verified market evidence "
                "was supplied for this request."
            )
        )

        common = f"""
You are working inside FX, a quantitative trading workstation.

The user does not code.

VERIFIED FX EVIDENCE:

{evidence}

Never invent prices, news, model results or strategy results.

The language model is not allowed to determine position size,
change risk limits or execute real-money trades.
"""

        kimi_messages = [
            {
                "role":"system",
                "content":
                    common
                    + """

You are the LEAD ANALYST.

Build the strongest evidence-based interpretation.

Identify:
- what the evidence supports
- opportunity
- uncertainty
- what should be checked next

Use clear English.
""",
            },
            {
                "role":"user",
                "content":
                    question,
            },
        ]

        critic_messages = [
            {
                "role":"system",
                "content":
                    common
                    + """

You are the INDEPENDENT RISK CRITIC.

Do not agree automatically.

Try to find:
- missing evidence
- conflicting signals
- overfitting
- stale data
- weak assumptions
- reasons NO TRADE may be better

Be concise.
""",
            },
            {
                "role":"user",
                "content":
                    question,
            },
        ]

        kimi_task = (
            asyncio.create_task(
                self._kimi(
                    kimi_messages
                )
            )
        )

        ollama_task = (
            asyncio.create_task(
                self._ollama(
                    critic_messages
                )
            )
        )

        kimi_view = None
        critic_view = None

        try:

            kimi_view = (
                await kimi_task
            )

        except Exception:

            kimi_view = None

        try:

            critic_view = (
                await asyncio.wait_for(
                    ollama_task,
                    timeout=45,
                )
            )

        except Exception:

            critic_view = None

        if (
            not kimi_view
            and not critic_view
        ):

            return {
                "provider": None,
                "model": None,
                "answer": (
                    "My AI committee is temporarily unavailable. "
                    "FX market data and deterministic models can still operate. "
                    "No trade was sent."
                ),
            }

        if not kimi_view:

            return {
                "provider":
                    "Ollama Risk Critic",

                "model":
                    self.ollama_model,

                "answer":
                    critic_view,
            }

        if not critic_view:

            return {
                "provider":
                    "Kimi",

                "model":
                    self.openrouter_model,

                "answer":
                    kimi_view,
            }

        chairman_messages = [
            {
                "role":"system",
                "content": """
You are the CHAIRMAN of the FX AI committee.

You receive:
1. A lead analyst view.
2. An independent risk critic view.

Reconcile them.

Never create new market facts.

Answer in plain English.

Use this structure when relevant:

WHAT FX SEES

WHY IT MATTERS

WHAT THE LOCAL CRITIC CHALLENGED

FX CONCLUSION

POSSIBLE ENTRY
only if verified evidence provides enough information

PROTECTION
only if verified risk calculations provide it

WHAT COULD GO WRONG

CURRENT MODE

NO TRADE is valid.
""",
            },
            {
                "role":"user",
                "content":
                    f"""
USER QUESTION:

{question}

VERIFIED EVIDENCE:

{evidence}

KIMI LEAD ANALYST:

{kimi_view}

OLLAMA LOCAL CRITIC:

{critic_view}
""",
            },
        ]

        try:

            final = await self._kimi(
                chairman_messages,
                max_tokens=900,
            )

        except Exception:

            final = (
                "KIMI ANALYSIS\n\n"
                + kimi_view
                + "\n\n"
                + "LOCAL RISK REVIEW\n\n"
                + critic_view
            )

        return {
            "provider":
                "FX AI Committee",

            "model":
                (
                    self.openrouter_model
                    + " + "
                    + self.ollama_model
                ),

            "answer":
                final,

            "committee":{
                "kimi":
                    kimi_view,

                "ollama":
                    critic_view,
            },
        }
