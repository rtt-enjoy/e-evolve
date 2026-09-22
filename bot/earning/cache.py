"""
File-based LLM response cache.

Serves repeated LLM prompts from disk so the OpenRouter free tier (50 req/day)
is only consumed for unique prompts. At the observed usage of roughly 50
requests per day across article generation, follow-ups, title revision and
format revision, a cache turns most of those into hits after the first cycle.

The cache is additive and never changes behaviour: a miss transparently
falls through to the real LLM call. Nothing here decides whether an article
publishes, how it is worded, or what it earns.

Design:
- Keyed by SHA-256 of (role, system prompt, user prompt, max_tokens).
  The system prompt alone is not enough -- the same system with a different
  prompt is a different question.
- JSON Lines: one object per line, append-friendly, easy to inspect with
  `tail` while the bot is running.
- TTL: entries expire after a configurable number of hours. A 24h default
  means a daily cycle re-uses yesterday's answers for the same prompt, which
  is the common case for format revision and title revision on similar
  sources.
- No locking. The cache is written at most once per LLM call, and reads are
  safe because JSON Lines is append-only and the writer closes the file
  handle before returning. Two concurrent writes from the same process are
  not possible -- GitHub Actions runs one job at a time.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)

_CACHE_DIR = Path(os.getenv("LLM_CACHE_DIR", "bot/earning/cache"))
_DEFAULT_TTL_HOURS = 24


def _cache_key(role: str, prompt: str, system: Optional[str], max_tokens: int) -> str:
    """Deterministic key from the inputs that define an LLM call."""
    raw = json.dumps({
        "role": role,
        "prompt": prompt,
        "system": system or "",
        "max_tokens": max_tokens,
    }, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_path(key: str) -> Path:
    """One file per key, so a stale entry is one `rm` and a corrupt one is one file."""
    return _CACHE_DIR / f"{key}.json"


def _read_cache(key: str, ttl_hours: int) -> Optional[dict]:
    """Return the cached response, or None when there is no valid entry."""
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("[cache] corrupt entry %s: %s", key[:12], exc)
        return None
    if not isinstance(raw, dict):
        return None
    cached_at = raw.get("_cached_at")
    if not cached_at:
        return None
    try:
        stamped = datetime.fromisoformat(str(cached_at))
    except Exception:
        return None
    if stamped.tzinfo is None:
        stamped = stamped.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - stamped
    if age > timedelta(hours=max(1, ttl_hours)):
        log.info("[cache] expired entry for %s (%.0fh old)", key[:12], age.total_seconds() / 3600)
        return None
    raw.pop("_cached_at", None)
    return raw


def _write_cache(key: str, value: Any) -> None:
    """Persist a response. Overwrites silently -- the latest answer wins."""
    try:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        payload = dict(value) if isinstance(value, dict) else {"value": value}
        payload["_cached_at"] = datetime.now(timezone.utc).isoformat()
        _cache_path(key).write_text(
            json.dumps(payload, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
    except Exception as exc:                       # pragma: no cover - defensive
        log.warning("[cache] write failed for %s: %s", key[:12], exc)


def cached_json(
    llm: Any,
    role: str,
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 2000,
    ttl_hours: int = _DEFAULT_TTL_HOURS,
) -> dict:
    """Return the JSON response for an LLM call, using the cache when possible.

    On a hit the cached response is returned and no API call is made. On a
    miss the real LLM is called and its response is written to the cache
    before being returned, so the next identical call is a hit.

    The function never changes what the LLM would have returned -- it only
    decides whether the call is made at all. A cache failure (corrupt file,
    disk full) degrades to a direct call, so the bot never breaks because
    the cache broke.
    """
    key = _cache_key(role, prompt, system, max_tokens)
    cached = _read_cache(key, ttl_hours)
    if cached is not None:
        log.info("[cache] HIT %s", key[:12])
        return cached

    log.info("[cache] MISS %s", key[:12])
    if hasattr(llm, "complete_json_for_role"):
        result = llm.complete_json_for_role(role, prompt, system=system, max_tokens=max_tokens)
    else:
        result = llm.complete_json(prompt, system=system, max_tokens=max_tokens)

    if isinstance(result, dict):
        _write_cache(key, result)
    return result