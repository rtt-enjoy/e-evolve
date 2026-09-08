"""
Receipt book — on-chain proof that money arrived.

Provides ``get_receipts(status)`` to read the receipt book and
``run(llm, status)`` as the product entry point the orchestrator calls,
wrapping ``attribution.record_receipt`` and ``attribution.summary``.
"""
from __future__ import annotations

import logging
from typing import Any

from . import attribution

log = logging.getLogger(__name__)


def get_receipts(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the receipt book entries, newest first."""
    book = status.get("attribution") or {}
    receipts = book.get("receipts", [])
    return list(receipts)


def run(llm: Any, status: dict[str, Any]) -> list[dict[str, Any]]:
    """Product entry point: record any new receipt and return the book.

    ``llm`` is accepted and deliberately unused — this module never makes
    a model call. The parameter exists only so the orchestrator can call
    this module the same way it calls the others.
    """
    record = attribution.record_receipt(status)
    summary = attribution.summary(status)

    if record:
        log.info(
            "[receipts] recorded +$%.6f (total: $%.6f, count: %d)",
            record.get("amount_usd", 0.0),
            summary.get("total_attributed_usd", 0.0),
            summary.get("receipt_count", 0),
        )
    else:
        log.debug("[receipts] no new receipt this cycle")

    return [{
        "platform": "receipts",
        "success": True,
        "receipt_count": summary.get("receipt_count", 0),
        "total_attributed_usd": summary.get("total_attributed_usd", 0.0),
        "last_receipt_at": summary.get("last_receipt_at"),
        "top_archetype": summary.get("top_archetype"),
        "estimated_usd": 0.0,
    }]