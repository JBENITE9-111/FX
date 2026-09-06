from __future__ import annotations

import asyncio
import os
import shutil
from typing import Any

import httpx
from openai import AsyncOpenAI


def _enabled(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


class FXLLMRouter:
    """Evidence-bound multi-brain committee. It can explain, never trade."""

    def __init__(self) -> None:
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "moonshotai/kimi-k2.6").strip()
        extras = os.getenv("OPENROUTER_COUNCIL_MODELS", "").split(",")
        self.openrouter_council_models = [item.strip() for item in extras if item.strip()][:3]
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:1.7b").strip()
        self.freellm_url = os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:3001/v1").rstrip("/")
        self.freellm_key = os.getenv("FREELLMAPI_API_KEY", "").strip()
        self.freellm_model = os.getenv("FREELLMAPI_MODEL", "fusion").strip()
        self.goose_path = os.getenv("GOOSE_PATH", "").strip() or shutil.which("goose") or ""
        self.goose_provider = os.getenv("GOOSE_PROVIDER", "openrouter").strip()
        self.goose_model = os.getenv("GOOSE_MODEL", "z-ai/glm-5.2:free").strip()

    async def _openai_compatible(self, base_url: str, api_key: str, model: str, messages: list[dict], max_tokens: int = 700) -> str:
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        response = await client.chat.completions.create(model=model, messages=messages, temperature=0.1, max_tokens=max_tokens)
        return response.choices[0].message.content or ""

    async def _openrouter(self, model: str, messages: list[dict], max_tokens: int = 700) -> str:
        if not self.openrouter_key:
            raise RuntimeError("OpenRouter is not configured")
        if _enabled("HEADROOM_ENABLED"):
            headroom_url = os.getenv("HEADROOM_BASE_URL", "http://127.0.0.1:8787").rstrip("/")
            try:
                return await self._openai_compatible(
                    f"{headroom_url}/v1", self.openrouter_key, model, messages, max_tokens
                )
            except Exception:
                pass
        return await self._openai_compatible("https://openrouter.ai/api/v1", self.openrouter_key, model, messages, max_tokens)

    async def _ollama(self, messages: list[dict]) -> str:
        if not _enabled("OLLAMA_ENABLED", True):
            raise RuntimeError("Ollama is disabled")
        timeout = httpx.Timeout(connect=5, read=90, write=20, pool=20)
        compact_messages = [
            {**message, "content": str(message.get("content", ""))[:6000]}
            for message in messages
        ]
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.ollama_url}/api/chat",
                json={"model": self.ollama_model, "messages": compact_messages, "stream": False, "think": False, "keep_alive": "30m", "options": {"temperature": 0.1, "num_predict": 220}},
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

    async def _freellm(self, messages: list[dict]) -> str:
        if not _enabled("FREELLMAPI_ENABLED"):
            raise RuntimeError("FreeLLMAPI is disabled")
        return await self._openai_compatible(self.freellm_url, self.freellm_key or "local-fx", self.freellm_model, messages)

    async def _goose(self, question: str, evidence: str) -> str:
        if not _enabled("GOOSE_CHAT_ENABLED") or not self.goose_path:
            raise RuntimeError("Goose is disabled or unavailable")
        system = (
            "You are a read-only peer analyst inside the FX research app. Lead with your own conclusion and "
            "challenge the other evidence-bound views supplied to you. Review only the supplied evidence. "
            "Do not use tools, browse, edit files, execute commands, or propose live trades. Identify unsupported "
            "claims and missing risk evidence. Never invent facts."
        )
        prompt = f"USER QUESTION:\n{question}\n\nVERIFIED FX EVIDENCE:\n{evidence[:12000]}"
        child_env = os.environ.copy()
        child_env.update({"GOOSE_MODE": "chat", "GOOSE_MAX_TOKENS": "350", "GOOSE_TELEMETRY_ENABLED": "false"})
        goose_path_root = os.path.abspath(
            os.getenv("GOOSE_PATH_ROOT", "").strip() or "data/goose_runtime"
        )
        os.makedirs(goose_path_root, mode=0o700, exist_ok=True)
        child_env["GOOSE_PATH_ROOT"] = goose_path_root
        if self.goose_provider == "openrouter" and self.openrouter_key:
            child_env["GOOSE_PROVIDER__API_KEY"] = self.openrouter_key
        process = await asyncio.create_subprocess_exec(
            self.goose_path, "run", "--provider", self.goose_provider, "--model", self.goose_model,
            "--no-profile", "--no-session", "--quiet", "--system", system, "--instructions", "-",
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
            env=child_env,
        )
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(input=prompt.encode("utf-8")), timeout=75)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError("Goose reviewer timed out")
        if process.returncode != 0:
            raise RuntimeError("Goose reviewer failed")
        answer = stdout.decode("utf-8", errors="replace").strip()
        if not answer:
            raise RuntimeError("Goose returned no review")
        return answer[-8000:]

    @staticmethod
    async def _settle(name: str, model: str, awaitable) -> dict | None:
        try:
            answer = await awaitable
            return {"name": name, "model": model, "answer": answer} if answer.strip() else None
        except Exception:
            return None

    async def _ask_member(
        self,
        kind: str,
        model: str,
        messages: list[dict],
        question: str,
        evidence: str,
    ) -> str:
        if kind == "openrouter":
            return await self._openrouter(model, messages)
        if kind == "ollama":
            return await self._ollama(messages)
        if kind == "freellm":
            return await self._freellm(messages)
        if kind == "goose":
            return await self._goose(question, evidence)
        raise RuntimeError(f"Unknown committee member kind: {kind}")

    async def reason(self, question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        evidence = str(context) if context else "No verified market evidence was supplied."
        common = (
            "You are part of the FX quantitative research committee. Use only VERIFIED FX EVIDENCE. "
            "Never invent prices, news, provider health, confidence, strategy results, or approvals. "
            "No language model can size risk, change limits, execute trades, or bypass deterministic risk. "
            "NO_TRADE is valid.\n\nVERIFIED FX EVIDENCE:\n" + evidence[:18000]
        )
        peer_prompt = [
            {
                "role": "system",
                "content": common + "\nYou are an equal peer lead and challenger. Produce your own conclusion, test the assumptions, identify disagreements and uncertainty, and state the next evidence needed.",
            },
            {"role": "user", "content": question},
        ]
        specs = [("Kimi", "openrouter", self.openrouter_model), ("Ollama", "ollama", self.ollama_model)]
        specs.extend((f"OpenRouter peer {index}", "openrouter", model) for index, model in enumerate(self.openrouter_council_models, 1))
        if _enabled("FREELLMAPI_ENABLED"):
            specs.append(("FreeLLMAPI fusion", "freellm", self.freellm_model))
        if _enabled("GOOSE_CHAT_ENABLED"):
            specs.append(("Goose", "goose", f"{self.goose_provider}/{self.goose_model}"))

        first_tasks = [
            self._settle(name, model, self._ask_member(kind, model, peer_prompt, question, evidence))
            for name, kind, model in specs
        ]
        first_views = [item for item in await asyncio.gather(*first_tasks) if item]
        first_names = {item["name"] for item in first_views}
        initial_missing = [spec for spec in specs if spec[0] not in first_names]
        if initial_missing:
            compact_initial = [
                {"role": "system", "content": common[:5000] + "\nEqual-peer retry: lead with a concise conclusion and challenge the evidence. Never invent facts or authorize a trade."},
                {"role": "user", "content": question},
            ]
            retry_initial = [
                self._settle(name, model, self._ask_member(kind, model, compact_initial, question, evidence[:5000]))
                for name, kind, model in initial_missing
            ]
            first_views.extend(item for item in await asyncio.gather(*retry_initial) if item)
        if not first_views:
            return {"provider": None, "model": None, "answer": "My AI committee is temporarily unavailable. Deterministic FX services can still operate. No trade was sent.", "committee": []}

        for view in first_views:
            view["completed_rounds"] = 1
        shared = "\n\n".join(f"{view['name']} ({view['model']}):\n{view['answer'][:2500]}" for view in first_views)
        debate_prompt = [
            {
                "role": "system",
                "content": common + "\nYou are an equal peer lead and challenger in round two. Review every peer view, challenge unsupported claims, acknowledge valid corrections, and give your revised conclusion. No member has authority over another.",
            },
            {"role": "user", "content": f"QUESTION:\n{question}\n\nROUND ONE PEER VIEWS:\n{shared[:10000]}"},
        ]
        active = {(view["name"], view["model"]) for view in first_views}
        second_tasks = [
            self._settle(
                name,
                model,
                self._ask_member(kind, model, debate_prompt, question, f"{evidence}\n\nROUND ONE:\n{shared}"),
            )
            for name, kind, model in specs
            if (name, model) in active
        ]
        revised = [item for item in await asyncio.gather(*second_tasks) if item]
        revised_names = {item["name"] for item in revised}
        missing_specs = [spec for spec in specs if spec[0] in {item["name"] for item in first_views} and spec[0] not in revised_names]
        if missing_specs:
            compact_debate = [
                {
                    "role": "system",
                    "content": common[:5000] + "\nEqual-peer retry: challenge the peer views and give a concise revised conclusion. Never invent facts or authorize a trade.",
                },
                {"role": "user", "content": f"QUESTION:\n{question}\n\nPEER VIEWS:\n{shared[:4000]}"},
            ]
            retry_tasks = [
                self._settle(
                    name,
                    model,
                    self._ask_member(kind, model, compact_debate, question, f"{evidence[:4000]}\n\nPEERS:\n{shared[:4000]}"),
                )
                for name, kind, model in missing_specs
            ]
            revised.extend(item for item in await asyncio.gather(*retry_tasks) if item)
        revised_by_name = {item["name"]: {**item, "completed_rounds": 2} for item in revised}
        views = [revised_by_name.get(item["name"], item) for item in first_views]
        final = "FX PEER COMMITTEE\nAll listed members led, challenged the shared evidence, and revised their view.\n\n" + "\n\n".join(
            f"{view['name']} ({view['model']}):\n{view['answer']}" for view in views
        )
        return {
            "provider": "FX Multi-Brain Committee",
            "model": " + ".join(view["model"] for view in views),
            "answer": final,
            "committee": views,
            "responding_brains": len(views),
            "configured_brains": len(specs),
            "full_initial_participation": len(first_views) == len(specs),
            "deliberation_rounds": 2 if revised else 1,
            "full_two_round_participation": bool(views) and all(item["completed_rounds"] == 2 for item in views),
        }
