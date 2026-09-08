"""
Receipt book reader and product entry point.

Provides:
  - get_receipts(status) -> list[dict]: read the attribution receipt book
  - run(llm, status) -> list[dict]: product entry point the orchestrator calls,
    wraps attribution.record_receipt and attribution.summary
"""
from __future__ import annotations

import logging
from typing import Any

from . import attribution

log = logging.getLogger(__name__)


def get_receipts(status: dict[str, Any]) -> list[dict]:
    """Return the receipt book entries from status.attribution."""
    book = status.get("attribution") or {}
    return list(book.get("receipts", []))


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Product entry point: record a receipt if money arrived, then return summary."""
    results: list[dict] = []
    
    # Record receipt if wallet received money this cycle
    record = attribution.record_receipt(status)
    if record:
        results.append({
            "platform": "receipts",
            "success": True,
            "recorded": True,
            "amount_usd": record.get("amount_usd", 0.0),
            "estimated_usd": 0.0,
        })
    
    # Always return the current attribution summary
    summary = attribution.summary(status)
    results.append({
        "platform": "receipts",
        "success": True,
        "summary": summary,
        "estimated_usd": 0.0,
    })
    
    return results