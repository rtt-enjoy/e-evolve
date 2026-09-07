"""
Earning Module — Receipts (attribution)

Reads the receipt book written by ``attribution`` and exposes it as a product.
The orchestrator calls ``run(llm, status)``; it records any new receipt and
returns an action describing the outcome.

Activates with: nothing. This module is pure bookkeeping and needs no secret.
"""
from __future__ import annotations

import logging
from typing import Any

from . import attribution

log = logging.getLogger(__name__)

_PLATFORM = "receipts"


def get_receipts(status: dict[str, Any]) -> dict[str, Any]:
    """Return the receipt book summary, or an empty summary if none."""
    return attribution.summary(status)


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Product entry point: record any new receipt and report the summary."""
    record = attribution.record_receipt(status)
    summary = attribution.summary(status)

    if record:
        log.info(
            "[receipts] recorded +$%.6f against %d live posts",
            float(record.get("amount_usd") or 0.0),
            (record.get("context") or {}).get("posts_live", 0),
        )
        return [{
            "platform": _PLATFORM,
            "success": True,
            "receipt_count": summary.get("receipt_count", 0),
            "total_attributed_usd": summary.get("total_attributed_usd", 0.0),
            "amount_usd": float(record.get("amount_usd") or 0.0),
            "estimated_usd": 0.0,
            "title": "Receipt recorded",
            "url": "",
        }]

    return [{
        "platform": _PLATFORM,
        "success": True,
        "skipped": True,
        "receipt_count": summary.get("receipt_count", 0),
        "total_attributed_usd": summary.get("total_attributed_usd", 0.0),
        "estimated_usd": 0.0,
        "title": "No new receipt this cycle",
        "url": "",
    }]