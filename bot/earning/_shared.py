from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

CONFIG_FILE = Path("config/strategy.json")

# --- Model validation and fallback -----------------------------------------
# When a provider decommissions a model (as Groq did with llama-3.1-70b-versatile
# on 2026-09-17), the evolution engine fails with a JSON parse error because no
# provider can fulfil the request. These functions catch that early and fall back
# to a known-good alternative instead of letting the error propagate.

MODEL_FALLBACKS: dict[str, dict[str, Any]] = {
    "groq": {
        "current": "llama-3.3-70b-versatile",
        "fallbacks": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "decommissioned": ["llama-3.1-70b-versatile"],
        "status_page": "https://console.groq.com/docs/deprecations",
    },
    "openrouter": {
        "current": "openrouter/free",
        "fallbacks": ["openrouter/auto"],
        "decommissioned": [],
    },
    "anthropic": {
        "current": "claude-3-5-sonnet-20241022",
        "fallbacks": ["claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "decommissioned": [],
    },
    "cerebras": {
        "current": "cerebras/big-bytemamba-7b",
        "fallbacks": ["cerebras/llama-3.1-8b"],
        "decommissioned": [],
    },
    "gemini": {
        "current": "gemini-2.5-flash",
        "fallbacks": ["gemini-2.0-flash"],
        "decommissioned": [],
    },
}


def validate_model(provider: str, model: str) -> bool:
    """Return True when ``model`` is known to be available on ``provider``.

    A model listed in ``decommissioned`` for its provider is known to be
    unavailable. Everything else is assumed available unless the provider's
    status page says otherwise -- this is a guard against known-bad models,
    not a live health check.
    """
    cfg = MODEL_FALLBACKS.get(provider)
    if cfg is None:
        return True
    return model not in cfg.get("decommissioned", [])


def get_fallback_model(provider: str, current: str | None = None) -> str | None:
    """Return a known-good model for ``provider``.

    If ``current`` is supplied and is not decommissioned, it is returned
    unchanged. Otherwise the provider's configured current model is returned,
    followed by each fallback in order. Returns None when the provider is
    unknown or has no known-good models.
    """
    cfg = MODEL_FALLBACKS.get(provider)
    if cfg is None:
        return None

    if current and current not in cfg.get("decommissioned", []):
        return current

    if current not in cfg.get("decommissioned", []):
        return cfg.get("current")

    for fallback in cfg.get("fallbacks", []):
        if fallback not in cfg.get("decommissioned", []):
            return fallback

    return None


def check_provider_health(provider: str, model: str) -> dict[str, Any]:
    """Validate a provider/model pair and return a health dict.

    Used before an LLM call so a decommissioned model is caught early with a
    clear message instead of a cryptic JSON parse error.
    """
    cfg = MODEL_FALLBACKS.get(provider)
    decommissioned = cfg.get("decommissioned", []) if cfg else []

    if model in decommissioned:
        status_page = cfg.get("status_page", "") if cfg else ""
        return {
            "healthy": False,
            "provider": provider,
            "model": model,
            "reason": "model decommissioned",
            "suggestion": get_fallback_model(provider, model),
            "status_page": status_page,
        }

    return {
        "healthy": True,
        "provider": provider,
        "model": model,
        "reason": "",
        "suggestion": None,
        "status_page": "",
    }


def load_config(section: str, defaults: Mapping[str, Any] | None = None) -> dict:
    """Return one section of the strategy file, with ``defaults`` filled in.

    Read at call time, never at import time. A module-level constant captured
    at import cannot see an owner's config edit without a reimport, and it
    forces tests to monkeypatch globals to change one setting.

    A missing or malformed file yields the defaults: bad config degrades the
    module to its documented behaviour rather than crashing the cycle.
    """
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get(section, {})
    except Exception:
        raw = {}
    cfg = dict(defaults or {})
    if isinstance(raw, dict):
        cfg.update(raw)
    return cfg


def hours_until_due(state: Mapping[str, Any], key: str, interval_hours: int) -> float:
    """Hours remaining before ``key``'s cadence is due again. 0.0 when due now.

    A missing or unparseable stamp reads as due. A module that has never run
    must be allowed to run, and a corrupt timestamp must not wedge it forever.
    """
    stamp = str(state.get(key) or "").strip()
    if not stamp:
        return 0.0
    last = parse_dt(stamp)
    if last is None:
        return 0.0
    due = last + timedelta(hours=max(1, interval_hours))
    return max(0.0, (due - datetime.now(timezone.utc)).total_seconds() / 3600)


def parse_dt(value: Any) -> Optional[datetime]:
    """Parse ISO-8601, RFC-822 (RSS ``pubDate``) or a unix epoch into aware UTC.

    Feeds serve all three, so all three are tried. A naive result is assumed
    UTC, which is what every source here publishes. The epoch branch exists
    because the remote-job APIs report ``pubDate`` as an integer, and without
    it a fresh posting reads as having no date at all.
    """
    if not value:
        return None
    raw = str(value).strip()
    # Epoch seconds. Bounded below so a bare year like "2026" cannot parse as
    # a timestamp in 1970, and above so milliseconds are not read as seconds.
    if re.fullmatch(r"\d{9,11}", raw):
        try:
            return datetime.fromtimestamp(int(raw), timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def strip_html(value: str) -> str:
    """Flatten feed HTML to plain text.

    ``<script>`` bodies are dropped whole -- tag-stripping alone would leave
    the JavaScript source behind as if it were prose.

    Entities are *decoded*, not deleted. Replacing them with a space used to
    corrupt the text it was meant to clean: Hacker News serves "$120-160/hr"
    as ``$120-160&#x2F;hr``, so a rate a human actually typed came out as
    "$120-160 hr" and no downstream reader could recognise it as a price.
    Numeric entities were not matched at all, leaving raw ``&#x2F;`` in place.
    """
    value = re.sub(r"<script.*?</script>", " ", value, flags=re.DOTALL | re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def xml_text(parent: ET.Element, tag: str) -> str:
    """Text of the first ``tag`` child, namespace-agnostic. '' when absent."""
    element = parent.find(f"{{*}}{tag}")
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def bounded_append(entries: list, value: Any, limit: int) -> None:
    """Append ``value`` if new, then trim ``entries`` to the newest ``limit``.

    Every history list in status.json is bounded this way so the file cannot
    grow without end across an hourly schedule.
    """
    if value and value not in entries:
        entries.append(value)
    del entries[: -max(1, limit)]