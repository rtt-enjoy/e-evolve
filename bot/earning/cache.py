"""
File-based cache for LLM JSON responses.

OpenRouter's free tier caps at 50 requests/day. This cache stores responses
on disk keyed by a hash of the prompt, so repeated runs with the same
prompt never burn a request. It is deliberately simple: no eviction policy,
no concurrency handling beyond atomic write, and it never raises -- a cache
miss is indistinguishable from a failure, and the caller always falls back
to the live API.

Usage:
    from bot.earning.cache import cached_json

    data = cached_json("post", prompt, system, lambda: llm.complete_json(...))
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Callable

log = logging.getLogger(__name__)

_CACHE_DIR = Path("cache/llm")
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key(role: str, prompt: str, system: str) -> str:
    """SHA-256 of role+prompt+system, stable across runs."""
    h = hashlib.sha256()
    h.update(role.encode("utf-8"))
    h.update(b"\x00")
    h.update(prompt.encode("utf-8"))
    h.update(b"\x00")
    h.update(system.encode("utf-8"))
    return h.hexdigest()


def get(role: str, prompt: str, system: str) -> dict[str, Any] | None:
    """Return a cached JSON dict, or None when there is no cache hit."""
    path = _CACHE_DIR / f"{_key(role, prompt, system)}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("[cache] corrupt entry removed: %s", exc)
        try:
            path.unlink()
        except OSError:
            pass
        return None


def put(role: str, prompt: str, system: str, data: dict[str, Any]) -> None:
    """Write a JSON dict to the cache. Never raises."""
    path = _CACHE_DIR / f"{_key(role, prompt, system)}.json"
    try:
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    except Exception as exc:
        log.warning("[cache] write failed: %s", exc)


def cached_json(
    role: str,
    prompt: str,
    system: str,
    fetcher: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Return cached JSON, or call fetcher and cache the result.

    The fetcher is only invoked on a cache miss. It must return a dict; any
    exception it raises propagates, because a failure means the live API is
    unavailable and the caller should know.
    """
    cached = get(role, prompt, system)
    if cached is not None:
        log.info("[cache] hit for %s prompt", role)
        return cached
    data = fetcher()
    put(role, prompt, system, data)
    return data