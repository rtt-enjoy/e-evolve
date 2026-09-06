"""Public receipt book for the dashboard.

Deterministic projection of ``attribution.receipts`` -- no LLM call, no
invented rows, bounded to the same history as attribution. This is the only
file needed for the dashboard surface; ``bot.dashboard.write_html`` consumes
it on the next evolution.
"""
from __future__ import annotations

from typing import Any

from . import _shared

DEFAULTS: dict[str, Any] = {
    "history_limit": 200,
}


def get_receipts(status: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the receipt book from status, bounded to the configured limit."""
    cfg = _shared.load_config("attribution", DEFAULTS)
    book = status.get("attribution") or {}
    receipts: list[dict[str, Any]] = book.get("receipts", [])
    limit = int(cfg.get("history_limit") or DEFAULTS["history_limit"])
    return receipts[-limit:] if len(receipts) > limit else receipts


def summary(status: dict[str, Any]) -> dict[str, Any]:
    """Return a compact summary of the receipt book."""
    receipts = get_receipts(status)
    return {
        "receipt_count": len(receipts),
        "total_usd": round(
            sum(float(r.get("amount_usd", 0)) for r in receipts), 6),
        "last_receipt_at": (receipts[-1].get("at") if receipts else None),
    }


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Return the receipt book as an action result.

    Deterministic -- reads numbers the attribution loop already fetched.
    No LLM call, no invented rows.
    """
    receipts = get_receipts(status)
    return [{
        "platform": "receipts",
        "success": True,
        "receipt_count": len(receipts),
        "total_usd": round(
            sum(float(r.get("amount_usd", 0)) for r in receipts), 6),
    }]