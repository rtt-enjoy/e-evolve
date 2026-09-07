"""
Receipt projection for the dashboard.

The attribution module writes a receipt record to ``status['attribution']['receipts']]
whenever real on-chain money arrives. This module reads that book and exposes it
as ``get_receipts(status)`` for the dashboard to consume. The ``run(llm, status)``
entry point follows the product pattern but never makes an LLM call -- this is
pure bookkeeping.

Design rules:
- **Deterministic. No LLM call.** Reads numbers the other loops already fetched.
- **Never raises.** A broken receipt book is still a receipt book.
- **Bounded.** Returns at most ``history_limit`` receipts, matching the
  attribution module's own bound.
"""
from __future__ import annotations

import logging
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    "history_limit": 200,
}


def config() -> dict[str, Any]:
    """This module's slice of config/strategy.json, read at call time."""
    return _shared.load_config("attribution", DEFAULTS)


def get_receipts(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the receipt book, bounded to the configured history limit.

    Returns [] when no receipts exist or the attribution section is absent.
    """
    book = status.get("attribution") or {}
    receipts: list[dict[str, Any]] = book.get("receipts", [])
    limit = int(config().get("history_limit") or DEFAULTS["history_limit"])
    if limit <= 0:
        return receipts
    if len(receipts) > limit:
        return receipts[-limit:]
    return receipts


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Product entry point: ``run(llm, status)``, like every other product.

    ``llm`` is accepted and deliberately unused. This module never makes a
    model call -- it only reads the receipt book that the attribution loop
    already wrote. The parameter exists only so the orchestrator can call
    this module the same way it calls the others.

    Returns a single action dict summarising the receipt book.
    """
    receipts = get_receipts(status)
    total = round(sum(float(r.get("amount_usd", 0.0)) for r in receipts), 6)

    return [{
        "platform": "receipts",
        "success": True,
        "receipt_count": len(receipts),
        "total_usd": total,
        # Observing receipts is not receiving money. Real revenue is the
        # on-chain balance, only ever that.
        "estimated_usd": 0.0,
        "title": f"Receipt book read ({len(receipts)} receipts, ${total:.6f})",
    }]