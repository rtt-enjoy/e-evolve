from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

_GROQ_MAX_PROMPT_TOKENS = 8_000
_CHARS_PER_TOKEN = 3.5

_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
]
_ANTHROPIC_MODELS = [
    "claude-sonnet-4-6",
    "claude-3-5-sonnet-20241022",
    "claude-3-haiku-20240307",
]
_GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]
# OpenRouter: strong free-tier models first, paid fallback
_OPENROUTER_MODELS = [
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "openai/gpt-4o-mini",
]

# Role → preferred provider mapping.
# Callers use complete_for_role() to get role-appropriate routing.
ROLE_PROVIDER: dict[str, str] = {
    "upgrade":  "gemini",
    "research": "openrouter",
    "post":     "groq",
    "think":      "gemini",
    "fast":       "groq",
    "experiment": "openrouter",
}


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    latency_s: float


class LLMClient:
    """Unified LLM client. Raises RuntimeError at init if no key is available."""

    def __init__(self) -> None:
        self._anthropic_key  = os.getenv("ANTHROPIC_API_KEY",  "").strip()
        self._gemini_key     = os.getenv("GEMINI_API_KEY",     "").strip()
        self._openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self._groq_key       = os.getenv("GROQ_API_KEY",       "").strip()
        self.provider        = self._pick_provider()
        self.model           = self._pick_model()
        self.info            = {"provider": self.provider, "model": self.model}
        log.info("LLM ready -- provider=%s model=%s", self.provider, self.model)

    # -- Public API ------------------------------------------------------------

    def complete(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a prompt, return LLMResponse. Retries 3x then falls back to next provider."""
        providers_to_try = self._provider_chain()
        last_exc: Exception | None = None

        for provider in providers_to_try:
            p_prompt  = self._truncate_for_groq(prompt, system, max_tokens) if provider == "groq" else prompt
            p_model   = self._model_for_provider(provider)
            exhausted = False

            for attempt in range(1, 4):
                try:
                    if provider == "anthropic":
                        return self._call_anthropic(p_prompt, system, max_tokens, temperature, p_model)
                    if provider == "gemini":
                        return self._call_gemini(p_prompt, system, max_tokens, temperature, p_model)
                    if provider == "openrouter":
                        return self._call_openrouter(p_prompt, system, max_tokens, temperature, p_model)
                    if provider == "claude-cli":
                        return self._call_claude_cli(p_prompt, system, max_tokens)
                    return self._call_groq(p_prompt, system, max_tokens, temperature, p_model)
                except Exception as exc:
                    last_exc = exc
                    exc_str  = str(exc)

                    # Auth errors: no point retrying same provider
                    if any(code in exc_str for code in ("401", "403", "authentication_error", "invalid x-api-key", "invalid_api_key", "API_KEY_INVALID")):
                        log.warning("LLM auth error on provider=%s -- skipping to fallback: %s", provider, exc)
                        exhausted = True
                        break

                    # Rate limit / quota exhausted: skip provider immediately
                    if any(code in exc_str for code in ("429", "rate_limit_exceeded", "RESOURCE_EXHAUSTED", "quota_exceeded", "RateLimitError", "insufficient_quota", "Too Many Requests")):
                        log.warning("LLM rate limit on provider=%s -- skipping to fallback: %s", provider, exc)
                        exhausted = True
                        break

                    # 413: truncate and retry (Groq only)
                    if "413" in exc_str and provider == "groq" and attempt < 3:
                        cutoff   = int(len(p_prompt) * 0.6)
                        nl       = p_prompt.rfind("\n", 0, cutoff)
                        p_prompt = p_prompt[: nl if nl > 0 else cutoff]
                        log.warning("LLM 413 attempt %d -- truncated to %d chars", attempt, len(p_prompt))
                        continue

                    # Model deprecated: advance to next in chain
                    if "model_not_found" in exc_str or "model not found" in exc_str.lower():
                        model_list = _model_list_for(provider)
                        if p_model in model_list:
                            idx = model_list.index(p_model)
                            if idx < len(model_list) - 1:
                                p_model = model_list[idx + 1]
                                log.warning("%s model deprecated -- advancing to %s", provider, p_model)
                                continue

                    log.warning("LLM attempt %d/3 provider=%s failed: %s", attempt, provider, exc)
                    if attempt < 3:
                        time.sleep(2 ** attempt)
                    else:
                        exhausted = True

            if exhausted and providers_to_try.index(provider) < len(providers_to_try) - 1:
                log.warning("LLM provider=%s exhausted -- trying fallback", provider)

        raise RuntimeError(f"LLM failed on all providers: {last_exc}") from last_exc

    def complete_for_role(
        self,
        role: str,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Route to role-appropriate provider (upgrade→gemini, research→openrouter, post→groq).
        Falls back to complete() with default provider if role provider unavailable."""
        preferred = ROLE_PROVIDER.get(role)
        if preferred:
            key_map = {
                "gemini":     self._gemini_key,
                "groq":       self._groq_key,
                "openrouter": self._openrouter_key,
                "anthropic":  self._anthropic_key,
            }
            if key_map.get(preferred):
                log.info("Role=%s → provider=%s", role, preferred)
                old_provider = self.provider
                self.provider = preferred
                try:
                    return self.complete(prompt, system=system, max_tokens=max_tokens,
                                        temperature=temperature)
                finally:
                    self.provider = old_provider
        return self.complete(prompt, system=system, max_tokens=max_tokens,
                             temperature=temperature)

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

    def complete_json_for_role(
        self,
        role: str,
        prompt: str,
        system: str = "",
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Like complete_json() but routes to role-appropriate provider."""
        json_system = (
            (system + "\n\n" if system else "")
            + "IMPORTANT: Respond with ONLY a single valid JSON object. "
            "No markdown, no code fences, no explanation before or after."
        )
        last_exc: Exception | None = None
        for attempt in range(1, 4):
            try:
                resp = self.complete_for_role(
                    role, prompt, system=json_system,
                    max_tokens=max_tokens, temperature=0.2,
                )
                return parse_json(resp.text)
            except (ValueError, RuntimeError) as exc:
                last_exc = exc
                log.warning("JSON[role=%s] attempt %d/3 failed: %s", role, attempt, exc)
                if attempt < 3:
                    time.sleep(1)
        raise ValueError(f"Could not get valid JSON from LLM (role={role}): {last_exc}") from last_exc

    # -- Groq ------------------------------------------------------------------

    def _truncate_for_groq(self, prompt: str, system: str, max_tokens: int) -> str:
        system_tokens    = len(system) / _CHARS_PER_TOKEN
        response_budget  = max_tokens
        available_chars  = int(
            (_GROQ_MAX_PROMPT_TOKENS - system_tokens - response_budget) * _CHARS_PER_TOKEN
        )
        if len(prompt) > available_chars > 0:
            log.info(
                "Groq prompt pre-truncated from %d to %d chars (token budget)",
                len(prompt), available_chars,
            )
            return prompt[:available_chars] + "\n... [truncated for token limit]"
        return prompt

    def _call_groq(
        self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
    ) -> LLMResponse:
        from groq import Groq  # lazy import
        client   = Groq(api_key=self._groq_key)
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        t0  = time.monotonic()
        rsp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return LLMResponse(
            text      = rsp.choices[0].message.content or "",
            provider  = "groq",
            model     = model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # -- Anthropic -------------------------------------------------------------

    def _call_anthropic(
        self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
    ) -> LLMResponse:
        import anthropic  # lazy import
        client = anthropic.Anthropic(api_key=self._anthropic_key)
        kwargs: dict[str, Any] = {
            "model":       model,
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
            model     = model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # -- Gemini ----------------------------------------------------------------

    def _call_gemini(
        self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
    ) -> LLMResponse:
        import google.generativeai as genai  # lazy import
        genai.configure(api_key=self._gemini_key)
        gen_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        # system_instruction supported on gemini-1.5+ and gemini-2.0+
        kwargs: dict[str, Any] = {"generation_config": gen_config}
        if system:
            kwargs["system_instruction"] = system
        t0     = time.monotonic()
        client = genai.GenerativeModel(model, **kwargs)
        rsp    = client.generate_content(prompt)
        return LLMResponse(
            text      = rsp.text or "",
            provider  = "gemini",
            model     = model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # -- OpenRouter ------------------------------------------------------------

    def _call_openrouter(
        self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
    ) -> LLMResponse:
        import requests  # already in requirements
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        t0  = time.monotonic()
        rsp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization":  f"Bearer {self._openrouter_key}",
                "HTTP-Referer":   "https://github.com/rtt-enjoy/e-evolve",
                "X-Title":        "e-evolve",
                "Content-Type":   "application/json",
            },
            json={
                "model":       model,
                "messages":    messages,
                "max_tokens":  max_tokens,
                "temperature": temperature,
            },
            timeout=90,
        )
        if rsp.status_code in (401, 403):
            raise RuntimeError(f"401 authentication_error from openrouter: {rsp.text[:200]}")
        if rsp.status_code == 429:
            raise RuntimeError(f"429 rate_limit_exceeded from openrouter: {rsp.text[:200]}")
        rsp.raise_for_status()
        data = rsp.json()
        if "error" in data:
            raise RuntimeError(f"OpenRouter error: {data['error']}")
        text = data["choices"][0]["message"]["content"] or ""
        return LLMResponse(
            text      = text,
            provider  = "openrouter",
            model     = model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # -- Claude CLI (Pro subscription, no API key) -----------------------------

    def _call_claude_cli(
        self, prompt: str, system: str, max_tokens: int
    ) -> LLMResponse:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        t0 = time.monotonic()
        result = subprocess.run(
            ["claude", "-p", full_prompt],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            stderr = result.stderr[:400]
            if "401" in stderr or "authentication" in stderr.lower() or "api key" in stderr.lower():
                raise RuntimeError(f"401 authentication_error from claude CLI: {stderr}")
            raise RuntimeError(f"claude CLI exited {result.returncode}: {stderr}")
        text = result.stdout.strip()
        if not text:
            raise RuntimeError("claude CLI returned empty response")
        return LLMResponse(
            text      = text,
            provider  = "claude-cli",
            model     = self.model,
            latency_s = round(time.monotonic() - t0, 2),
        )

    # -- Helpers ---------------------------------------------------------------

    def _pick_provider(self) -> str:
        if os.getenv("CLAUDE_CLI_MODE", "").strip() == "1":
            return "claude-cli"
        if self._anthropic_key:
            return "anthropic"
        # Gemini preferred for default (hard thinking role)
        if self._gemini_key:
            return "gemini"
        if self._openrouter_key:
            return "openrouter"
        if self._groq_key:
            return "groq"
        raise RuntimeError(
            "No LLM API key found.\n"
            "Add one of: ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, GROQ_API_KEY\n"
            "to GitHub -> Settings -> Secrets and variables -> Actions.\n"
            "For local dev with Claude Pro: set CLAUDE_CLI_MODE=1 in .env"
        )

    def _pick_model(self) -> str:
        return self._model_for_provider(self.provider)

    def _model_for_provider(self, provider: str) -> str:
        if provider == "anthropic":
            return _ANTHROPIC_MODELS[0]
        if provider == "gemini":
            return _GEMINI_MODELS[0]
        if provider == "openrouter":
            return _OPENROUTER_MODELS[0]
        if provider == "claude-cli":
            return "claude-sonnet-4-6"
        return _GROQ_MODELS[0]

    def _provider_chain(self) -> list[str]:
        """Ordered fallback chain starting from primary provider."""
        all_providers = [
            ("claude-cli",   os.getenv("CLAUDE_CLI_MODE", "").strip() == "1"),
            ("anthropic",    bool(self._anthropic_key)),
            ("gemini",       bool(self._gemini_key)),
            ("openrouter",   bool(self._openrouter_key)),
            ("groq",         bool(self._groq_key)),
        ]
        available = [p for p, has_key in all_providers if has_key]
        # Ensure primary is first
        if self.provider in available:
            available.remove(self.provider)
            available.insert(0, self.provider)
        return available


def _model_list_for(provider: str) -> list[str]:
    return {
        "groq":        _GROQ_MODELS,
        "anthropic":   _ANTHROPIC_MODELS,
        "gemini":      _GEMINI_MODELS,
        "openrouter":  _OPENROUTER_MODELS,
    }.get(provider, [])


# -- JSON parser (module-level so tests can import directly) ------------------

def parse_json(text: str) -> dict[str, Any]:
    """
    Parse JSON from an LLM response string.
    Handles markdown fences, leading/trailing prose.
    Raises ValueError if no valid JSON object found.
    """
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n?```\s*$',          '', text, flags=re.MULTILINE)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start != -1:
        decoder = json.JSONDecoder()
        try:
            obj, _ = decoder.raw_decode(text, start)
            return obj
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON object found in LLM response. First 200 chars: {text[:200]!r}")
