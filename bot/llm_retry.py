"""
Retry-once helper for research-role LLM calls.

A single transient provider blip (429, 5xx, timeout) is the most common reason
an evolution cycle skips an upgrade. Wrapping one research-role call in a
second attempt on the same prompt turns most blips into successes, with no
new secret, no new dependency, and no change to the orchestrator or the
provider modules.

Scope is deliberately small: only the research role is wrapped here, because
the two callers that justified this helper -- ``code_techs._online_ai_brief``
and ``mrr_ideas._viability_brief`` -- both already gate on a single research
call. A wider retry policy belongs in ``bot.llm``; this file stays the
minimum change that fixes the observed failure.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

log = logging.getLogger(__name__)

# One retry, one short sleep. The point is to absorb a single 429/5xx blip,
# not to mask a sustained outage -- a second failure must still surface so
# the caller can fall through to its deterministic-triage fallback.
_MAX_ATTEMPTS = 2
_RETRY_SLEEP_SECONDS = 2.0

# Message fragments that suggest a transient failure worth one retry. Permanent
# failures (auth, model withdrawn, schema rejection) must NOT be retried -- they
# will fail identically the second time and just waste a free-tier request.
_TRANSIENT_FRAGMENTS = (
    "429",
    "rate limit",
    "timeout",
    "timed out",
    "temporarily",
    "try again",
    "connection reset",
    "connection aborted",
    "remote disconnected",
    "502",
    "503",
    "504",
    "500 internal",
    "service unavailable",
)


def _looks_transient(exc: BaseException) -> bool:
    """True when a failure reads as a transient provider blip.

    Network exceptions are always transient. Application errors (auth, schema,
    model-not-found) only retry when the message itself looks like a brief
    outage; otherwise a second attempt just burns a free-tier request.
    """
    name = type(exc).__name__.lower()
    if any(tag in name for tag in ("timeout", "connection", "network")):
        return True
    msg = str(exc).lower()
    return any(frag in msg for frag in _TRANSIENT_FRAGMENTS)


def research_call(llm: Any, prompt: str, *, max_tokens: int = 3000) -> Any:
    """Call the LLM's research role once, retrying once on transient blips.

    Returns the parsed JSON object on success, or ``None`` on any failure --
    callers already treat a missing brief as "use the deterministic fallback",
    so ``None`` is the correct sentinel here.
    """
    if llm is None:
        return None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            if hasattr(llm, "complete_json_for_role"):
                return llm.complete_json_for_role(
                    "research", prompt, max_tokens=max_tokens)
            return llm.complete_json(prompt, max_tokens=max_tokens)
        except Exception as exc:
            if attempt >= _MAX_ATTEMPTS or not _looks_transient(exc):
                log.warning(
                    "[llm_retry] research call failed (attempt %d/%d): %s",
                    attempt, _MAX_ATTEMPTS, exc)
                return None
            log.info(
                "[llm_retry] transient research failure (attempt %d/%d): %s -- retrying once",
                attempt, _MAX_ATTEMPTS, exc)
            time.sleep(_RETRY_SLEEP_SECONDS)
    return None