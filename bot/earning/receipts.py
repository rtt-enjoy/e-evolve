"""
Receipt book reader and product entry point.

Provides:
  - get_receipts(status) -> list[dict]: read the attribution receipt book
  - run(llm, status) -> list[dict]: product entry point called by orchestrator,
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
    """Product entry point: record any new receipt and return attribution summary."""
    results: list[dict] = []
    
    # Record receipt if wallet received money this cycle
    record = attribution.record_receipt(status)
    if record:
        results.append({
            "platform": "attribution",
            "success": True,
            "receipt_recorded": True,
            "amount_usd": record.get("amount_usd", 0.0),
            "estimated_usd": 0.0,
        })
    
    # Always return current attribution summary
    summary = attribution.summary(status)
    results.append({
        "platform": "attribution",
        "success": True,
        "summary": summary,
        "estimated_usd": 0.0,
    })
    
    return results