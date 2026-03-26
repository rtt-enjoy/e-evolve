"""
LLM Client
Abstracts Groq (free/fast) and Anthropic (Claude, higher quality).
Auto-selects based on which API key is present.
Priority: Anthropic if ANTHROPIC_API_KEY is set, else Groq.

All external imports are lazy so the module loads even when
groq/anthropic are not yet installed.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

# Model lists — first entry is preferred; fallback if API rejects it
_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",        # smallest fallback
]
_ANTHROPIC_MODELS = [
    "claude-sonnet-4-6",
    "claude-3-5-sonnet-20241022",
    "claude-3-haiku-20240307",
]


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    latency_s: float


class LLMClient:
    """Unified LLM client. Raises RuntimeError at init if no key is available."""

    def __init__(self) -> None:
        self._groq_key      = os.getenv("GROQ_API_KEY", "").strip()
        self._anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.provider       = self._pick_provider()
        self.model          = self._pick_model()
        self.info           = {"provider": self.provider, "model": self.model}
        log.info("LLM ready — provider=%s model=%s", self.provider, self.model)

    # ── Public API ─────────────────────────────────────────────────────────

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a prompt, return LLMResponse. Retries up to 3× on transient errors."""
        last_exc: Exception | None = None
        for attempt in range(1, 4):
            try:
                if self.provider == "anthropic":
                    return self._call_anthropic(prompt, system, max_tokens, temperature)
                return self._call_groq(prompt, system, max_tokens, temperature)
            except Exception as exc:
                last_exc = exc
                log.warning("LLM attempt %d/3 failed: %s", attempt, exc)
                if attempt < 3:
                    time.sleep(2 ** attempt)   # 2 s, 4 s
        raise RuntimeError(f"LLM failed after 3 attempts: {last_exc}") from last_exc

    def complete_json(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """
        Like complete() but parses the response as JSON.
        Appends a JSON-only instruction to the system prompt.
        Raises ValueError if JSON cannot be extracted after retries.
        """
        json_system = (
            (system + "\n\n" if system else "")
            + "IMPORTANT: Respond with ONLY a single valid JSON object. "
            "No markdown, no code fences, no explanation before or after."
        )
        last_exc: Exception | None = None
        for attempt in range(1, 4):
            try:
                resp = self.complete(
                    prompt, system=json_system,
                    max_tokens=max_tokens, temperature=0.2,
                )
                return parse_json(resp.text)
            except (ValueError, RuntimeError) as exc:
                last_exc = exc
                log.warning("JSON attempt %d/3 failed: %s", attempt, exc)
                if attempt < 3:
                    time.sleep(1)
        raise ValueError(f"Could not get valid JSON from LLM: {last_exc}") from last_exc

    # ── Groq ───────────────────────────────────────────────────────────────

    def _call_groq(
        self, prompt: str, system: str, max_tokens: int, temperature: float
    ) -> LLMResponse:
        from groq import Groq  # lazy import
        client = Groq(api_key=self._groq_key)
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        t0  = time.monotonic()
        rsp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return LLMResponse(
            text      = rsp.choices[0].message.content or "",
            provider  = "groq",
            model     = self.model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # ── Anthropic ──────────────────────────────────────────────────────────

    def _call_anthropic(
        self, prompt: str, system: str, max_tokens: int, temperature: float
    ) -> LLMResponse:
        import anthropic  # lazy import
        client = anthropic.Anthropic(api_key=self._anthropic_key)
        kwargs: dict[str, Any] = {
            "model":       self.model,
            "max_tokens":  max_tokens,
            "temperature": temperature,
            "messages":    [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        t0  = time.monotonic()
        msg = client.messages.create(**kwargs)
        return LLMResponse(
            text      = msg.content[0].text if msg.content else "",
            provider  = "anthropic",
            model     = self.model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _pick_provider(self) -> str:
        if self._anthropic_key:
            return "anthropic"
        if self._groq_key:
            return "groq"
        raise RuntimeError(
            "No LLM API key found.\n"
            "Add GROQ_API_KEY (free: console.groq.com) or ANTHROPIC_API_KEY\n"
            "to GitHub → Settings → Secrets and variables → Actions."
        )

    def _pick_model(self) -> str:
        return _ANTHROPIC_MODELS[0] if self.provider == "anthropic" else _GROQ_MODELS[0]


# ── JSON parser (module-level so tests can import directly) ─────────────────

def parse_json(text: str) -> dict[str, Any]:
    """
    Parse JSON from an LLM response string.
    Handles markdown fences, leading/trailing prose.
    Raises ValueError if no valid JSON object found.
    """
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```\s*$',          '', text, flags=re.MULTILINE)
    text = text.strip()

    # Strategy 1: the whole string is JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: find the outermost { ... } block
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON object found in LLM response. First 200 chars: {text[:200]!r}")
