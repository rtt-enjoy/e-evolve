from __future__ import annotations

"""
Standalone model-fallback module that can be imported by any earning module
or the evolution engine. Provides validate_model(), get_fallback_model(),
and check_provider_health() to catch decommissioned models before they
cause JSON parse errors.

Principle: detect decommissioned models early so the evolution engine can
swap in a known-good alternative without failing the entire cycle.
"""

MODEL_FALLBACKS: dict[str, dict[str, str]] = {
    "openrouter": {
        "llama-3.1-70b-versatile": "openrouter/free",
        "groq-llama-3.1-8b": "openrouter/free",
    },
    "groq": {
        "llama-3.1-70b-versatile": "openrouter/free",
        "mixtral-8x7b-32k-inst": "openrouter/free",
    },
    "anthropic": {
        "claude-3-opus-20240229": "openrouter/anthropic/claude-3-opus",
        "claude-3.5-sonnet-20240620": "openrouter/anthropic/claude-3-5-sonnet",
    },
    "cerebras": {
        "llama-3.1-70b-versatile": "openrouter/free",
        "mixtral-8x7b-32k-inst": "openrouter/free",
    },
}

VALIDATED_GOOD_MODELS: dict[str, str] = {
    "openrouter": "openrouter/free",
    "groq": "openrouter/free",
    "anthropic": "openrouter/anthropic/claude-3-5-sonnet",
    "cerebras": "openrouter/free",
}


def validate_model(provider: str, model: str) -> bool:
    """Return True when the model is known to be active and supported.

    Returns False when the provider-model combination is decommissioned
    or otherwise known to be unreliable. Modules should check before calling
    the LLM and fall back to get_fallback_model() when this returns False.
    """
    providers = MODEL_FALLBACKS.get(provider, {})
    if model not in providers:
        # Unknown model: assume valid (conservative) so we don't break
        # legitimate use of new models.
        return True
    # Model exists in fallback dict, meaning it was decommissioned or
    # problematic. Return False so callers can swap.
    return False


def get_fallback_model(provider: str, model: str) -> str | None:
    """Return a known-good alternative model for the given provider,
    or None when no fallback is available.

    The fallback is selected from MODEL_FALLBACKS[provider][model], which
    maps decommissioned/problematic models to known-good alternatives.
    """
    providers = MODEL_FALLBACKS.get(provider, {})
    if model in providers:
        return providers[model]
    # No known fallback for this model;
    # try the provider's default validated model.
    return VALIDATED_GOOD_MODELS.get(provider)


def check_provider_health(provider: str) -> dict[str, str]:
    """Return a health status dict for the given LLM provider.

    Useful for the evolution engine to log or decide whether to attempt
    a model swap mid-cycle.
    """
    fallbacks = MODEL_FALLBACKS.get(provider)
    if fallbacks:
        return {
            "status": "degraded",
            "note": f"Provider {provider} has decommissioned models mapped to fallbacks.",
        }
    return {"status": "unknown", "note": f"Provider {provider} not in MODEL_FALLBACKS."}


def suggest_fallback(provider: str, model: str) -> dict[str, str]:
    """Convenience function returning a ready-to-use fallback suggestion.

    Returns a dict with 'fallback_model' and 'reason' keys suitable for
    inclusion in evolution engine logs or decisions.
    """
    fallback = get_fallback_model(provider, model)
    if fallback:
        return {
            "fallback_model": fallback,
            "reason": f"Model {model} for {provider} is decommissioned; using {fallback} as alternative.",
        }
    return {
        "fallback_model": None,
        "reason": f"Model {model} for {provider} has no known fallback.",
    }