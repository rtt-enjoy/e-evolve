"""
Receipt book — the on-chain evidence of what readers actually paid.

Read-only projection of ``status["attribution"]["receipts"]``.
No LLM call, no network request, no mutation. The dashboard and
tests consume this module the same way they consume every other
product: ``run(llm, status)`` returns an action dict, and
``get_receipts(status)`` returns the receipt book.
"""
from __future__ import annotations

import logging
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

_DEFAULTS: dict[str, Any] = {
    "enabled": True,
    "history_limit": 200,
}


def config() -> dict[str, Any]:
    """This module's slice of config/strategy.json, read at call time."""
    return _shared.load_config("receipts", _DEFAULTS)


def get_receipts(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the receipt book, newest first, bounded by history_limit."""
    cfg = config()
    limit = int(cfg.get("history_limit") or _DEFAULTS["history_limit"])
    book = status.get("attribution") or {}
    receipts: list[dict[str, Any]] = list(book.get("receipts", []))
    return receipts[-limit:] if receipts else []


def run(llm: Any = None, status: dict | None = None) -> list[dict]:
    """Product entry point: ``run(llm, status)``, like every other product.

    ``llm`` is accepted and deliberately unused. This module never makes
    a model call -- it only projects the receipt book that ``attribution``
    already wrote into status. The parameter exists only so the orchestrator
    can call this module the same way it calls the others.

    Returns a single action dict with the receipt count, or [] when the
    module is disabled.
    """
    status = status if isinstance(status, dict) else {}
    cfg = config()
    if not cfg.get("enabled"):
        return []

    receipts = get_receipts(status)
    total = sum(float(r.get("amount_usd", 0) or 0) for r in receipts)

    return [{
        "platform": "receipts",
        "success": True,
        "receipt_count": len(receipts),
        "total_attributed_usd": round(total, 6),
        "estimated_usd": 0.0,
        "title": f"Receipt book: {len(receipts)} receipt(s), ${total:.6f} total",
    }]