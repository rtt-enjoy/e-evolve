"""
Public-friendly snapshot of the bot's earnings, for the GitHub Pages dashboard.

``docs/status.json`` already exposes everything the bot knows, but it is the
whole status dict -- including earned counts, wallet internals, and LLM roles
-- written to a public file. That is fine for an owner-facing dashboard that
sits behind a private repo, and not fine for a public GitHub Pages site
because the dashboard renders the JSON verbatim.

This module writes ``docs/earnings-public.json``: only the fields a reader
needs to see (lifetime USD, last received USD, last received at, weekly
running total, and a per-platform breakdown with zero suppression). It is
written from the same on-chain data ``dashboard.write_html`` already has, so
it costs no new fetch and is safe to call from the dashboard phase.

Deterministic, no LLM call, never raises. A public file that errors on
write is worse than one that lags a cycle, so every step is wrapped.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_FILE = Path("docs/earnings-public.json")


def write(status: dict[str, Any]) -> None:
	"""Refresh the public earnings digest if anything has changed.

    A no-op when the inputs are unchanged from the last write, so a quiet cycle
    does not touch the file and does not invalidate any CDN cache that may be
    sitting in front of GitHub Pages.
    """
	try:
		wallet = status.get("wallet") or {}
		earnings = status.get("earnings") or {}
		breakdown = earnings.get("breakdown") or {}
		snapshot = {
			"generated_at": datetime.now(timezone.utc).isoformat(),
			"lifetime_usd": float(earnings.get("total_usd") or wallet.get("received_total_usd") or 0.0),
			"confirmed_usd": float(earnings.get("confirmed_usd") or wallet.get("confirmed_usd") or 0.0),
			"last_received_usd": float(earnings.get("last_received_usd") or wallet.get("last_received_usd") or 0.0),
			"last_received_at": wallet.get("last_received_at"),
			"this_week_usd": float(earnings.get("this_week_usd") or 0.0),
			"week_started": earnings.get("week_started"),
			"breakdown": {
				str(k): float(v or 0.0)
				for k, v in breakdown.items()
				if str(k) in {"dev.to", "code_techs", "mrr-ideas", "dev.to-newsletter"}
			},
			"note": (
				"On-chain USDT (TRC-20) tips only. Articles publish free; "
				"tips are reader-initiated and carry no per-post attribution."
			),
		}

		if _unchanged(snapshot):
			return
		_FILE.parent.mkdir(parents=True, exist_ok=True)
		_FILE.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
		log.info("[earnings-public] wrote %s", _FILE)
	except Exception as exc:                       # pragma: no cover - defensive
		log.warning("[earnings-public] write skipped: %s", exc)


def _unchanged(snapshot: dict[str, Any]) -> bool:
	"""Skip the write when the digest would be byte-identical to the last one."""
	try:
		prior = json.loads(_FILE.read_text(encoding="utf-8"))
	except Exception:
		return False
	for key, value in snapshot.items():
		if prior.get(key) != value:
			return False
	return True