"""
Model fallback and validation for LLM calls.

Validates model identifiers before making LLM calls and falls back to a
stable default when a model is invalid or deprecated. This prevents
crashes from bad model names and reduces wasted free-tier calls on
unavailable models.
"""
from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger(__name__)

# Stable defaults per provider. These are models known to exist and be
# free or low-cost as of 2026-09.
_DEFAULT_MODELS: dict[str, str] = {
    "openrouter": "openrouter/free",
    "gemini": "gemini-2.5-flash",
    "groq": "groq/llama-3.3-70b-versatile",
    "anthropic": "anthropic/claude-3-haiku-20260307",
    "cerebras": "cerebras/llama3.1-8b",
}


def validate_model(provider: str, model: str) -> bool:
    """Return True when ``model`` looks like a valid identifier for ``provider``.

    This is a lightweight syntactic check, not a live API call. It catches
    the common failures (empty string, None, obviously malformed names)
    before the expensive LLM call is attempted.
    """
    if not model or not isinstance(model, str):
        log.warning("[model_fallback] invalid model for %s: %r", provider, model)
        return False
    # OpenRouter models must contain a "/" (e.g. "openrouter/free")
    if provider == "openrouter" and "/" not in model:
        log.warning("[model_fallback] openrouter model missing '/': %r", model)
        return False
    # Gemini models must not be empty after stripping
    if provider == "gemini" and not model.strip():
        return False
    # Cerebras models must contain "/"
    if provider == "cerebras" and "/" not in model:
        return False
    # Anthropic models must contain "/"
    if provider == "anthropic" and "/" not in model:
        return False
    # Groq models must contain "/"
    if provider == "groq" and "/" not in model:
        return False
    return True


def fallback_for_model(provider: str, model: str) -> str:
    """Return a stable default model for ``provider`` when ``model`` is invalid.

    Logs the fallback so the owner can see a model was replaced.
    """
    default = _DEFAULT_MODELS.get(provider, "")
    log.warning(
        "[model_fallback] model %r invalid for %s, falling back to %r",
        model, provider, default,
    )
    return default


def resolve_model(llm: object, provider: str, model: str) -> str:
    """Validate ``model`` and return a safe model string.

    If the model is invalid, returns the fallback for the provider.
    If the LLM client has a ``validate_model`` method, delegates to it
    for a live check; otherwise uses the syntactic check.
    """
    # Let the LLM client validate first if it can.
    if hasattr(llm, "validate_model"):
        try:
            if llm.validate_model(provider, model):
                return model
        except Exception as exc:
            log.warning("[model_fallback] LLM validation failed: %s", exc)

    if not validate_model(provider, model):
        return fallback_for_model(provider, model)
    return model