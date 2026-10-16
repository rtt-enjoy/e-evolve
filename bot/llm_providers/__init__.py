from __future__ import annotations

from typing import Any, Optional

from . import cerebras


def get_provider(name: str) -> Optional[Any]:
    """Return a provider module by name, or None if unavailable.

    Used by the orchestrator to resolve a provider string from
    config/strategy.json into a module that exposes
    ``complete_json`` and ``complete_json_for_role``.
    """
    providers = {
        "cerebras": cerebras,
    }
    return providers.get(name)


def complete_json(provider_name: str, prompt: str, system: str = "", max_tokens: int = 6000) -> Optional[dict]:
    """Dispatch a JSON-completion call to the named provider.

    Returns None if the provider is unknown or the call fails, so the
    caller can fall back to another provider.
    """
    provider = get_provider(provider_name)
    if provider is None:
        return None
    return provider.complete_json(prompt, system=system, max_tokens=max_tokens)


def complete_json_for_role(provider_name: str, role: str, prompt: str, system: str = "", max_tokens: int = 6000) -> Optional[dict]:
    """Dispatch a role-aware JSON-completion call to the named provider."""
    provider = get_provider(provider_name)
    if provider is None:
        return None
    return provider.complete_json_for_role(role, prompt, system=system, max_tokens=max_tokens)