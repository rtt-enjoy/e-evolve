"""
Earnings Tracker
Accumulates earnings, resets weekly counter on Monday UTC.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LOG_FILE = Path("earnings-log.md")


def _append_weekly_history(week_started: str, total_usd: float, breakdown: dict) -> None:
    bd_str = ", ".join(f"{k}: ${v:.4f}" for k, v in breakdown.items()) if breakdown else "none"
    line = f"\n## Week {week_started} — ${total_usd:.4f} ({bd_str})\n"
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


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

    today   = datetime.now(timezone.utc).date()
    current_week_monday = (today - timedelta(days=today.weekday())).isoformat()
    started = e.get("week_started") or current_week_monday

    # Reset whenever we've rolled into a new week (handles skipped weeks too)
    if started < current_week_monday:
        prev_amount = e.get("this_week_usd", 0)
        log.info("Week reset: this_week_usd was $%.4f (week started %s)", prev_amount, started)
        _append_weekly_history(started, prev_amount, e.get("breakdown", {}))
        e["this_week_usd"] = 0.0
        e["week_started"]  = current_week_monday
        e["breakdown"]     = {}

    if not e.get("week_started"):
        e["week_started"] = current_week_monday

    # Tally
    cycle: float = 0.0
    breakdown: dict[str, float] = e.setdefault("breakdown", {})

    for a in actions:
        if not a.get("success"):
            continue
        platform = a.get("platform", "unknown")
        amount   = float(a.get("estimated_usd") or 0) + float(a.get("pnl_usd") or 0)
        cycle   += amount
        breakdown[platform] = round(breakdown.get(platform, 0.0) + amount, 6)

    e["total_usd"]      = round(e.get("total_usd",      0.0) + cycle, 6)
    e["this_week_usd"]  = round(e.get("this_week_usd",  0.0) + cycle, 6)
    e["last_cycle_usd"] = round(cycle, 6)

    # Rolling history of last 48 non-zero cycles for trend display (2-day window)
    history: list = e.setdefault("history", [])
    # Purge any stale zeros left by earlier bugs or cold starts
    history[:] = [v for v in history if v > 0]
    if cycle > 0:
        history.append(round(cycle, 6))
    if len(history) > 48:
        history[:] = history[-48:]

    log.info("Earnings — cycle: +$%.4f | week: $%.4f | total: $%.4f",
             cycle, e["this_week_usd"], e["total_usd"])
    return status
