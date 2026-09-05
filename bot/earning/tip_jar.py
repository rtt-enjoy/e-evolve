"""
Earning Module — Tip Jar (dev.to)

Publishes a short article reminding readers that tips are welcome. Runs on a
cadence the owner can force, and only publishes once per state cycle unless
forced. Research and publishing only; no outreach, no payment processing.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from . import devto, payout

log = logging.getLogger(__name__)

_PLATFORM = "dev.to-tip-jar"

def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Publish a tip-jar article if one has not been published recently."""
    api_key = os.getenv("DEV_TO_API_KEY", "").strip()
    if not api_key:
        return []

    state = status.setdefault("tip_jar", {})
    if state.get("published") and not status.get("_overrides", {}).get("force_tip_jar"):
        log.info("[tip_jar] already published — skipping")
        return []

    article = {
        "title": "Support This Work — A Small USDT Tip Keeps These Articles Coming",
        "description": "These write-ups are researched and published with no paywall. A small USDT tip is welcome.",
        "body_markdown": (
            "## Support this work\n\n"
            "These articles are researched and published with no paywall, sponsor, or tracking. "
            "If one saved you an afternoon, a small USDT tip keeps them coming.\n\n"
            "You can send a tip to the address below.\n"
        ),
        "tags": ["support", "crypto", "devto"],
    }
    article = payout.add_footer(article)
    result = devto.publish(article, api_key)
    result["platform"] = _PLATFORM
    if result.get("success"):
        state["published"] = True
    return [result]