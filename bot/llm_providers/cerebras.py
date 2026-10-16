from __future__ import annotations

import logging
import os
from typing import Any, Optional

try:
    import requests
except ImportError:  # pragma: no cover - requests is a hard dep at runtime
    requests = None  # type: ignore[assignment]

log = logging.getLogger(__name__)

_API_BASE = "https://api.cerebras.ai/v1"
_TIMEOUT = 30


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "e-evolve-cerebras",
    }


def complete_json(prompt: str, system: str = "", max_tokens: int = 6000) -> Optional[dict]:
    """Call the Cerebras chat completions endpoint and return parsed JSON.

    Returns None when the key is missing, the request fails, or the response
    cannot be parsed as JSON. The caller is responsible for any fallback.
    """
    api_key = os.getenv("CEREBRAS_API_KEY", "").strip()
    if not api_key:
        log.debug("[cerebras] CEREBRAS_API_KEY not set — skipping")
        return None
    if requests is None:
        log.warning("[cerebras] requests not installed — skipping")
        return None

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "llama3.1-70b",  # Cerebras-hosted Llama 3.1 70B; verify current default
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{_API_BASE}/chat/completions",
            headers=_headers(api_key),
            json=payload,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            log.warning("[cerebras] empty content in response")
            return None
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # The model may have wrapped the JSON in a code fence.
            cleaned = content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
    except Exception as exc:
        log.warning("[cerebras] request failed: %s", exc)
        return None


def complete_json_for_role(role: str, prompt: str, system: str = "", max_tokens: int = 6000) -> Optional[dict]:
    """Role-aware wrapper so the orchestrator can call any provider uniformly.

    Cerebras does not differentiate roles, so this delegates to complete_json.
    """
    return complete_json(prompt, system=system, max_tokens=max_tokens)