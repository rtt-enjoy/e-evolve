# bot/earning/model_fallback.py
"""
Fallback model functions for LLM providers.

Provides default models and validation for LLM roles used by earning modules.
If the primary model is unavailable, falls back to a safe default.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# Default fallback model: openrouter/free (free tier, no credit card required)
_FALLBACK_MODEL = "openrouter/free"


def get_model(role: str) -> str:
    """
    Return a model identifier for the given role.

    The role is one of the LLM workflow purposes defined in status.json
    (e.g., "post", "research", "upgrade"). If a model for the role is known
    and active, it is returned; otherwise the fallback model is used.
    """
    # This implementation currently returns the fallback for all roles.
    # In a full implementation it would consult status["llm_workflows"].
    log.info("[model_fallback] using model %s for role %s", _FALLBACK_MODEL, role)
    return _FALLBACK_MODEL


def get_model_for_role(role: str) -> str:
    """Alias for get_model."""
    return get_model(role)


def validate_model(model: str) -> bool:
    """
    Validate that a model identifier is usable.

    Returns True if the model is non‑empty and looks like a known provider/model.
    """
    if not model:
        return False
    # Simple heuristic: contains a slash (provider/model) and is not a placeholder.
    if "/" not in model:
        return False
    # Optionally check against a list of known providers.
    known_providers = {"openrouter", "gemini", "groq", "anthropic", "cerebras"}
    provider = model.split("/", 1)[0].lower()
    return provider in known_providers


def fallback_for_model(role: str, error: Exception) -> str:
    """
    Return a fallback model when the primary model fails.

    Logs the error and returns the default fallback model.
    """
    log.warning(
        "[model_fallback] fallback for role %s due to %s",
        role,
        error,
    )
    return _FALLBACK_MODEL