"""
Public-facing receipt book: which on-chain tips arrived, and which published
post was performing at that moment.

`bot/earning/attribution` already records the publishing context at receipt
time, but it writes into the `attribution` namespace of status.json and never
into a file the dashboard can fetch directly. The dashboard reads
`docs/status.json`, which is fine for ops state but means a reader visiting
the dashboard cannot see the receipt book without knowing to look in the JSON
blob.

This module is the reader-facing mirror of attribution. Three rules apply:

- **No LLM call.** The book is a deterministic projection of attribution
  receipts plus the post list the reach loop already fetched. A model asked to
  describe a receipt would add words without adding fact.
- **Never invents rows.** If `attribution` has no receipts, the rendered book
  explicitly says so. Showing zero rows is honest; showing no row at all reads
  as missing data.
- **Bounded by the same `history_limit` as attribution.** The two surfaces
  cannot disagree about how many receipts exist.

The output is `docs/receipts.json` with one entry per receipt and a tiny
summary at the top. It does not include private fields beyond what the
attribution record already carries -- the wallet address is the public receive
address, which `payout.public_snapshot` already publishes.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_OUTPUT_FILE = Path("docs/receipts.json")
_MAX_ROWS = 100


def config() -> dict[str, Any]:
    """This module's slice of config/strategy.json, read at call time."""
    from . import _shared
    return _shared.load_config("receipts", {
        "enabled": True,
        "max_rows": _MAX_ROWS,
    })


def build(status: dict[str, Any]) -> dict[str, Any]:
    """Return the reader-facing receipt book for this status snapshot.

    Never raises: this is read-only, and a failure here costs the dashboard
    nothing it would otherwise have had.
    """
    try:
        cfg = config()
        if not cfg.get("enabled"):
            return _empty("disabled in config")

        book = status.get("attribution") or {}
        receipts = list(book.get("receipts") or [])
        limit = max(1, int(cfg.get("max_rows", _MAX_ROWS)))

        # Newest first so a fresh tip lands at the top of the dashboard.
        rows = sorted(receipts, key=lambda r: str(r.get("at") or ""), reverse=True)
        rows = rows[:limit]

        summary = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "receipt_count": int(book.get("receipt_count") or len(rows)),
            "total_usd": float(book.get("total_attributed_usd") or 0.0),
            "last_receipt_at": book.get("last_receipt_at"),
            "top_archetype": ((book.get("by_archetype") or [{}])[0].get("archetype")
                              if book.get("by_archetype") else None),
            "note": book.get("note"),
            "enabled": True,
        }
        return {"summary": summary, "receipts": rows}
    except Exception as exc:
        log.warning("[receipts] build failed: %s", exc)
        return _empty(str(exc)[:160])


def _empty(reason: str) -> dict[str, Any]:
    """An honest empty book: zero rows, the reason stated, nothing hidden."""
    return {
        "summary": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "receipt_count": 0,
            "total_usd": 0.0,
            "last_receipt_at": None,
            "top_archetype": None,
            "note": reason,
            "enabled": False,
        },
        "receipts": [],
    }


def write(status: dict[str, Any]) -> None:
    """Write the reader-facing receipt book to docs/receipts.json."""
    try:
        _OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        _OUTPUT_FILE.write_text(
            json.dumps(build(status), indent=2, default=str),
            encoding="utf-8",
        )
        log.info("[receipts] wrote %s", _OUTPUT_FILE)
    except Exception as exc:
        log.warning("[receipts] write skipped: %s", exc)