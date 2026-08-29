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
	# week_started may be None (a fresh status) or a non-string (corrupt write).
	# A non-string is never '<=' a real date, so the only safe fallback is to
	# treat the module as never having run and reset cleanly.
	started_raw = e.get("week_started")
	started = started_raw if isinstance(started_raw, str) and started_raw else current_week_monday

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

	# Real money, straight from the chain. Earning modules all report 0.0
	# because none of them pay; the only verifiable revenue is what has landed
	# on USDT_WALLET_ADDRESS. The dashboard shows these fields as "earned" and
	# the `*_usd` totals above as unrealised activity value.
	wallet = status.get("wallet") or {}
	e["confirmed_usd"]        = float(wallet.get("confirmed_usd") or 0.0)
	e["received_total_usd"]   = float(wallet.get("received_total_usd") or 0.0)
	e["last_received_usd"]    = float(wallet.get("last_received_usd") or 0.0)
	e["source"]               = "on-chain USDT balance"

	# Rolling history of real wallet receipts for the trend spark. Kept to the
	# last 48 non-zero entries. This tracks money in, not articles published —
	# the old version charted the fabricated per-article constant.
	history: list = e.setdefault("history", [])
	history[:] = [v for v in history if v > 0]
	if e["last_received_usd"] > 0:
		history.append(e["last_received_usd"])
	if len(history) > 48:
		history[:] = history[-48:]

	log.info("Earnings — on-chain confirmed: $%.6f | lifetime received: $%.6f "
			 "| this cycle received: +$%.6f",
			 e["confirmed_usd"], e["received_total_usd"], e["last_received_usd"])
	return status