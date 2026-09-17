"""
Model validation and fallback for LLM providers.

When a model is decommissioned (as happened with Groq's
llama-3.1-70b-versatile on 2026-09-17), the evolution engine fails with a
JSON parsing error because no provider can fulfil the request. This module
provides a way to validate models before use and fall back to known-good
alternatives automatically.

The fallback chain is checked in order: first the provider's current model,
then each fallback in turn. The first model that passes validation is
returned. If none pass, the caller is notified so it can raise the issue
explicitly rather than silently failing.

Usage:
    from bot.earning.model_fallback import validate_model, get_fallback_model

    if not validate_model(provider, model):
        model = get_fallback_model(provider, model) or model
"""
from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

# Known model configurations per provider. Updated when a provider
# announces a deprecation (check the provider's status page before
# editing).
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

    A model that appears in ``decommissioned`` for its provider is known to be
    unavailable. Everything else is assumed available unless the provider's
    status page says otherwise -- this function is a guard against known-bad
    models, not a live health check.
    """
    cfg = MODEL_FALLBACKS.get(provider)
    if cfg is None:
        # Unknown provider: assume available, the caller will find out when
        # the API call fails.
        return True
    if model in cfg.get("decommissioned", []):
        log.warning(
            "[model_fallback] %s is decommissioned on %s",
            model, provider,
        )
        return False
    return True


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

    Used by the evolution engine before attempting an LLM call so a
    decommissioned model is caught early with a clear message instead of a
    cryptic JSON parse error.
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