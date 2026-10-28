"""
Research Module -- CTF bounties.

The owner's standing research focus: Capture The Flag competitions that pay a
prize, ranked so a newcomer can enter one this week. Source is CTFtime's public
event API -- keyless, JSON, and the one calendar every CTF organiser lists on --
so this needs **no new secret**.

What this is and is not:

- **Research, not earning.** A CTF prize is paid for the owner's own solving,
  once per event. That is labour per unit, which fails doctrine Principle 2
  row 2: a job, not passive income. It is listed because the owner asked for
  it, and it never counts toward revenue -- the action reports
  ``estimated_usd: 0.0`` and real revenue stays the on-chain balance.
- **Never `channel`.** Nothing here is a place the bot's own product gets
  listed and paid for, so it does not touch the Leads queue in ``code_techs``.
- **Prize text is the organiser's claim.** CTFtime's ``prizes`` field is free
  text ("TBD", "$500", "Certificates"). ``pays`` and ``crypto`` read that text
  and nothing else; neither is a promise, and KYC / payout terms are not in the
  feed at all, so every event carries ``kyc: "not published"``. The owner has
  no way to pass an identity check, so the rules page has to be read before
  registering.
- Suggestion-only and deterministic: no LLM call, nothing is registered,
  submitted, or posted.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import requests

from ._shared import hours_until_due, load_config, parse_dt

log = logging.getLogger(__name__)

_API = "https://ctftime.org/api/v1/events/"
# CTFtime answers 403 to the default python-requests agent.
_HEADERS = {"User-Agent": "e-evolve-research-bot/1.0 (+https://github.com)"}

_DEFAULTS = {
	"enabled": True,
	"refresh_hours": 6,
	# Events starting up to this many days out are considered.
	"lookahead_days": 45,
	# Events that started up to this many days ago and are still running count.
	"running_grace_days": 3,
	"fetch_limit": 100,
	# Rows kept in status.json. It is committed hourly, so this is a size cap.
	"status_max_items": 14,
	"prize_max_chars": 160,
}

# A figure, a currency word, or an explicit cash/bounty/crypto prize. "TBD",
# "Certificates" and "Swag" must not match: an unannounced prize is not a prize.
_MONEY = re.compile(
	r"[$€£]\s?\d|\d\s?[$€£]|\d[\d,.]*\s?(?:k\b|usd|eur|gbp|usdt|usdc|dollars?|euros?)"
	r"|\bcash\b|\bprize\s+pool\b|\bbounty\b|\bbtc\b|\beth\b|\bcrypto",
	re.I,
)
_CRYPTO = re.compile(
	r"\b(?:usdt|usdc|btc|bitcoin|eth|ethereum|sol|solana|stablecoin|crypto(?:currency)?)\b",
	re.I,
)
_NO_PRIZE = re.compile(r"^\s*(?:tbd|tba|none|n/?a|no prizes?|-)?\s*$", re.I)
_BEGINNER = re.compile(
	r"\b(?:beginner|newbie|novice|entry[- ]level|introductory|first[- ]time|"
	r"for students|high[- ]school|junior)s?\b",
	re.I,
)


def config() -> dict:
	"""Strategy config for this module. Read per call, never at import."""
	return load_config("ctf_bounty", _DEFAULTS)


def _state(status: dict) -> dict:
	return status.setdefault("ctf_bounty", {})


def fetch_events(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""Raw CTFtime events, or ``None`` when the feed could not be read.

	``None`` is not ``[]``: an unreadable feed must not look like a quiet
	month, because the caller keeps the last good list on the first and
	replaces it on the second.
	"""
	start = now - timedelta(days=int(cfg["running_grace_days"]))
	finish = now + timedelta(days=int(cfg["lookahead_days"]))
	try:
		resp = requests.get(
			_API,
			params={
				"limit": int(cfg["fetch_limit"]),
				"start": int(start.timestamp()),
				"finish": int(finish.timestamp()),
			},
			headers=_HEADERS,
			timeout=20,
		)
		resp.raise_for_status()
		data = resp.json()
	except Exception as exc:
		log.warning("[ctf_bounty] CTFtime fetch failed: %s", exc)
		return None
	return data if isinstance(data, list) else None


def _prize_text(raw: Any, limit: int) -> str:
	text = re.sub(r"\s+", " ", str(raw or "")).strip()
	return text[:limit]


def build_event(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	"""One ranked row from one CTFtime event, or ``None`` when it is not enterable.

	Enterable means online, open to anyone, and not already over. An onsite
	final or a prequalified bracket is real, and no use to this owner.
	"""
	start, finish = parse_dt(str(raw.get("start") or "")), parse_dt(str(raw.get("finish") or ""))
	if start is None or finish is None or finish < now:
		return None
	if raw.get("onsite"):
		return None
	if str(raw.get("restrictions") or "Open").strip().lower() != "open":
		return None

	prizes = _prize_text(raw.get("prizes"), int(cfg["prize_max_chars"]))
	pays = bool(prizes) and not _NO_PRIZE.match(prizes) and bool(_MONEY.search(prizes))
	crypto = pays and bool(_CRYPTO.search(prizes))
	title = str(raw.get("title") or "").strip()
	blob = f"{title} {raw.get('description') or ''}"
	jeopardy = str(raw.get("format") or "").strip().lower() == "jeopardy"
	beginner = bool(_BEGINNER.search(blob))

	live = start <= now
	days_out = max(0.0, (start - now).total_seconds() / 86400)
	score = 0
	score += 40 if pays else 0
	score += 25 if crypto else 0
	# Jeopardy (independent challenges) is the entry format; attack-defence
	# needs a team and infrastructure.
	score += 10 if jeopardy else 0
	score += 15 if beginner else 0
	score += 10 if live else 8 if days_out <= 7 else 4 if days_out <= 21 else 0

	return {
		"id": raw.get("id"),
		"title": title,
		"url": str(raw.get("url") or raw.get("ctftime_url") or ""),
		"ctftime_url": str(raw.get("ctftime_url") or ""),
		"start": start.isoformat(),
		"finish": finish.isoformat(),
		"live": live,
		"days_until_start": round(days_out, 1),
		"format": str(raw.get("format") or "").strip(),
		"weight": raw.get("weight"),
		"participants": raw.get("participants"),
		"prizes": prizes,
		"pays": pays,
		"crypto": crypto,
		"beginner": beginner,
		# Not in the feed. Stated out loud so an absent field cannot read as "none".
		"kyc": "not published",
		"score": score,
	}


def build_events(raw_events: list[dict], cfg: dict, now: datetime) -> list[dict]:
	rows = [row for raw in raw_events if isinstance(raw, dict) and (row := build_event(raw, cfg, now))]
	# Soonest first within a score, so a tie reads as "what can I enter next".
	rows.sort(key=lambda r: (-r["score"], r["start"]))
	return rows


def run(llm: Any = None, status: Optional[dict] = None) -> list[dict]:
	"""Refresh the CTF list. ``llm`` is accepted and unused (see module docstring)."""
	status = status if isinstance(status, dict) else {}
	cfg = config()
	state = _state(status)
	action: dict[str, Any] = {"platform": "ctf-bounty", "success": False, "estimated_usd": 0.0}

	if not cfg.get("enabled"):
		state["last_reason"] = "disabled"
		return []

	if hours_until_due(state, "last_refresh_at", int(cfg["refresh_hours"])) > 0:
		return []

	now = datetime.now(timezone.utc)
	raw = fetch_events(cfg, now)
	if raw is None:
		# Keep the last good list; say plainly that it is stale.
		state["last_reason"] = "fetch_failed"
		action["error"] = "CTFtime API unreachable"
		return [action]

	rows = build_events(raw, cfg, now)
	state.update({
		"source": "ctftime",
		"last_refresh_at": now.isoformat(),
		"last_reason": "ok",
		"fetched": len(raw),
		"enterable": len(rows),
		"paying": sum(1 for r in rows if r["pays"]),
		"crypto": sum(1 for r in rows if r["crypto"]),
		"beginner": sum(1 for r in rows if r["beginner"]),
		"events": rows[: int(cfg["status_max_items"])],
	})
	action.update({"success": True, "listed": len(state["events"])})
	log.info(
		"[ctf_bounty] %d fetched, %d enterable, %d with a stated prize",
		len(raw), len(rows), state["paying"],
	)
	return [action]
