"""
Earnings Tracker
Accumulates earnings, resets weekly counter on Monday UTC.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)


def update(status: dict[str, Any], actions: list[dict]) -> dict[str, Any]:
    """
    Tally this cycle's successful earning actions into the status dict.
    Resets this_week_usd automatically on Mondays.
    Returns updated status.
    """
    e = status.setdefault("earnings", {
        "total_usd":      0.0,
        "this_week_usd":  0.0,
        "last_cycle_usd": 0.0,
        "week_started":   None,
        "breakdown":      {},
    })

    today   = datetime.now(timezone.utc).date().isoformat()
    started = e.get("week_started") or today

    # Monday reset (isoweekday 1 = Monday)
    if datetime.now(timezone.utc).isoweekday() == 1 and started < today:
        log.info("Monday reset: this_week_usd was $%.4f", e.get("this_week_usd", 0))
        e["this_week_usd"] = 0.0
        e["week_started"]  = today

    if not e.get("week_started"):
        e["week_started"] = today

    # Tally
    cycle: float = 0.0
    breakdown: dict[str, float] = e.setdefault("breakdown", {})

    for a in actions:
        if not a.get("success"):
            continue
        platform = a.get("platform", "unknown")
        amount   = float(a.get("estimated_usd", 0)) + float(a.get("pnl_usd", 0))
        cycle   += amount
        breakdown[platform] = round(breakdown.get(platform, 0.0) + amount, 6)

    e["total_usd"]      = round(e.get("total_usd",      0.0) + cycle, 6)
    e["this_week_usd"]  = round(e.get("this_week_usd",  0.0) + cycle, 6)
    e["last_cycle_usd"] = round(cycle, 6)

    log.info("Earnings — cycle: +$%.4f | week: $%.4f | total: $%.4f",
             cycle, e["this_week_usd"], e["total_usd"])
    return status
