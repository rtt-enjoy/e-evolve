"""
Deterministic USDT payout verification.

Confirms the configured TRC-20 wallet address matches the one published
in article footers. A mismatch would silently break all tips -- this
check catches that drift each cycle without any LLM call.

Records the result in status.json under "payout_consistency" so a
mismatch is a visible structural zero rather than a quiet failure.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)


def verify(status: dict[str, Any]) -> dict[str, Any]:
    """Run the payout consistency check.

    Reads the configured USDT_WALLET_ADDRESS and compares it with the
    address published in payout_public. Records the result under
    ``payout_consistency`` and returns it.

    This is deterministic -- no LLM call, no network request.
    """
    configured = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    payout_public = status.get("payout_public", {})
    published_address = payout_public.get("address", "")

    mismatch = bool(configured and published_address and configured != published_address)

    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "configured_address": configured,
        "published_address": published_address,
        "match": not mismatch,
        "mismatch": mismatch,
    }

    status["payout_consistency"] = result

    if mismatch:
        log.warning(
            "[payout_verify] MISMATCH: configured %s != published %s",
            configured,
            published_address,
        )
    else:
        log.info("[payout_verify] address consistency verified")

    return result