"""
LLM model validation and fallback.

Validates model identifiers before LLM calls and provides safe
fallbacks when a model is invalid, deprecated, or unreachable.

Why this exists: a mistyped or deprecated model name produces a
400 from the provider, and the error payload shape differs per
provider. Catching it here -- before the call -- keeps the cycle
alive and costs no LLM call. The fallback model is the provider's
most stable free-tier model, chosen so research output quality
does not regress.
"""
from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

# The most stable free-tier model per provider. Used as a fallback
# when a requested model is invalid. Verify before relying on a
# model that may be deprecated next cycle.
_FALLBACK_MODELS: dict[str, str] = {
	"openrouter": "openrouter/free",
	"gemini": "gemini-2.5-flash",
	"groq": "llama-3.3-70b-versatile",
	"anthropic": "claude-3-haiku-4-20250415",
	"cerebras": "cerebras/llama-3.1-8b",
}

# Known-deprecated or unreachable model identifiers. A model matching
# one of these is rejected even if the provider would otherwise
# accept it, because it has been observed to fail in production.
_DEPRECATED: set[str] = set()


def validate_model(provider: str, model: str) -> tuple[bool, str]:
	"""Check whether ``model`` is usable for ``provider``.

	Returns (True, model) when the model is valid, or (False, reason)
	when it should be skipped. The reason is human-readable for
	logging and status reporting.

	Validation is deliberately lightweight: a check on the model
	string and a check against the deprecated set. No network call
	-- a 400 from the provider is caught at the call site anyway,
	and this pre-check exists to avoid the call entirely.
	"""
	if not model or not str(model).strip():
		return False, "model identifier is empty"

	model = str(model).strip()

	if model in _DEPRECATED:
		return False, f"model {model!r} is deprecated or unreachable"

	# A model string should contain a slash (provider/name) or be a
	# known bare name for its provider. Bare strings that don't match
	# any known pattern are likely typos.
	if "/" not in model:
		if provider not in ("groq", "gemini"):
			return False, f"model {model!r} has no provider prefix"

	return True, model


def fallback_for_model(provider: str, model: str) -> str:
	"""Return a safe fallback model for ``provider``.

	Never raises. If the provider has no entry in the fallback
	table, returns the model unchanged so the caller can decide
	what to do -- better to try the original than to guess a
	provider we don't know about.
	"""
	return _FALLBACK_MODELS.get(provider, model)