"""
Payout address consistency verification.

A silent mismatch between the configured USDT_WALLET_ADDRESS and the address
actually rendered in the article footer would break every tip without any
visible error -- the footer would still look correct, just point somewhere
else. This module catches that drift deterministically each cycle.

No LLM call. No network call. It compares the address the wallet loop
already resolved against the one the payout footer already renders, and
records the result in status["payout_consistency"].
"""
from __future__ import annotations

import logging
import os
from typing import Any

from . import payout

log = logging.getLogger(__name__)


def verify(status: dict[str, Any]) -> dict[str, Any]:
	"""Confirm the configured wallet address matches the published footer.

	Returns a dict with:
	  - ``configured``: the address from USDT_WALLET_ADDRESS (masked)
	  - ``published``: the address the footer actually renders (masked)
	  - ``match``: True when both are present and equal
	  - ``checked_at``: ISO timestamp

	A mismatch is a structural zero (doctrine Principle 3h): tips sent to the
	wrong address cannot be recovered, so this must be visible in status.json
	rather than only in logs.
	"""
	configured = (os.getenv("USDT_WALLET_ADDRESS") or "").strip()
	published = payout.wallet_address()

	result = {
		"configured": _mask(configured),
		"published": _mask(published),
		"match": bool(configured and published and configured == published),
		"checked_at": _now_iso(),
	}

	if not configured:
		result["error"] = "USDT_WALLET_ADDRESS is not set"
		log.warning("[payout_verify] USDT_WALLET_ADDRESS is not set")
	elif not published:
		result["error"] = "payout footer has no wallet address"
		log.warning("[payout_verify] payout footer has no wallet address")
	elif not result["match"]:
		result["error"] = "configured address does not match published footer"
		log.error("[payout_verify] MISMATCH: configured %s != published %s", result["configured"], result["published"])
	else:
		log.info("[payout_verify] payout address consistent")

	status["payout_consistency"] = result
	return result


def _mask(address: str) -> str:
	"""Mask an address for status.json: first 6 + ... + last 4."""
	if not address or len(address) < 10:
		return address or ""
	return f"{address[:6]}...{address[-4:]}"


def _now_iso() -> str:
	from datetime import datetime, timezone
	return datetime.now(timezone.utc).isoformat()