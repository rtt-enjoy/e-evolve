"""
Receipts product — reads the on-chain attribution ledger.

Provides:
  get_receipts(status) -> list[dict]  -- all recorded receipts, newest first
  run(llm, status) -> list[dict]       -- product entry point; records a receipt if money arrived

The orchestrator calls run() each cycle. It delegates to attribution.record_receipt
(which writes a receipt when wallet.last_received_usd > 0) and returns the
attribution summary for the dashboard.
"""
from __future__ import annotations

import logging
from typing import Any

from . import attribution

log = logging.getLogger(__name__)


def get_receipts(status: dict[str, Any]) -> list[dict]:
    """Return all receipts from the attribution book, newest first."""
    book = status.get("attribution") or {}
    receipts = book.get("receipts", [])
    # Newest first for display
    return list(reversed(receipts))


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Product entry point: record a receipt if money arrived, return summary."""
    # Record a receipt if the wallet saw new money this cycle
    record = attribution.record_receipt(status)
    summary = attribution.summary(status)
    
    result = {
        "platform": "receipts",
        "success": True,
        "receipt_recorded": record is not None,
        "receipt": record,
        "summary": summary,
        "estimated_usd": 0.0,
    }
    
    if record:
        log.info("[receipts] recorded new receipt: $%.6f", record.get("amount_usd", 0.0))
    
    return [result]