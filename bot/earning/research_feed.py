"""
Research Module -- prize and bounty feeds beyond CTF.

Owner directive, 2026-11-05: the Research page showed CTF bounties only. This
module widens it to the other places a solo developer can win a stated prize,
each from a keyless public JSON feed, so it needs **no new secret and no LLM
call**:

- ``hackathon``     Devpost -- online hackathons with a stated cash prize.
- ``crypto-bounty`` Superteam Earn -- bounties paid in a stablecoin.
- ``bug-bounty``    Immunefi -- web3 bug bounty programs. The feed states whether
                    a program asks for KYC, which is the owner's binding constraint.
- ``challenge``     DEV's own challenge announcements (``devteam`` on dev.to).

CTFs stay in ``ctf_bounty`` (Overview reads that key); the Research page reads
both and shows one list.

What this is and is not:

- **Research, not earning.** A prize is paid for the owner's own work, once.
  That is labour per unit, which fails doctrine Principle 2 row 2. Every action
  reports ``estimated_usd: 0.0``, nothing is summed, and nothing here is ever a
  ``channel`` in the Leads queue. Real revenue is the on-chain balance.
- **A prize is the organiser's claim.** ``prize`` is shown as the source wrote it.
  ``kyc`` is ``"not published"`` unless the source states it (Immunefi does).
- **Every row says when it was added.** ``discovered_at`` comes from a
  first-seen ledger over the whole candidate pool, not from the previous
  displayed list, so a row a size cap drops and a later refresh brings back
  keeps its stamp instead of reading "just now". The source's own clock
  (``posted_at``, ``starts_at``, ``deadline``) is kept apart from it.
- **Nothing prohibited, ever** (owner rule, 2026-11-03). Every row passes
  ``_shared.prohibited_category`` before it reaches status.
- **An unreadable feed is not an empty one.** A fetcher returns ``None`` on any
  failure and the last good rows of that source are kept.

Probed and left out (do not re-probe): Sherlock (the live page is finished
contests, and it requires KYC), HackerOne ``bounty-targets-data`` (19 MB, undated,
ID-gated payouts), GitHub ``label:bounty`` (bot spam and "send one real email"
tasks), Devfolio (onsite in India), Algora and DoraHacks (HTML / WAF challenge),
Cantina (no public API).
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

import requests

from ._shared import (
	hours_until_due,
	load_config,
	parse_dt,
	prohibited_category,
	select_fresh_first,
	stamp_from_ledger,
	strip_html,
)

log = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "e-evolve-research-bot/1.0 (+https://github.com)"}

_DEFAULTS = {
	"enabled": True,
	"refresh_hours": 3,
	# Hackathons and bounties starting further out than this are not listed.
	"lookahead_days": 60,
	# Rows kept per category in status.json (committed hourly, so a size cap).
	"per_category_cap": 16,
	# Share of each category's slots reserved for rows first listed recently,
	# newest first, ahead of the score cut. 0 gives a plain score ranking.
	"min_fresh_share": 0.5,
	"fresh_hours": 72,
	"devpost_pages": 3,
	# The announcement carries no deadline field and challenges run one to three
	# weeks, so an old one may be closed. The page shows when it was announced.
	"challenge_max_age_days": 7,
	# How long the first-seen ledger remembers a row that left the pool.
	"ledger_days": 45,
	"ledger_max_entries": 500,
	"text_max_chars": 110,
}

CATEGORIES: dict[str, str] = {
	"hackathon": "Hackathons",
	"crypto-bounty": "Crypto bounties",
	"bug-bounty": "Bug bounties",
	"challenge": "Dev challenges",
}

_CRYPTO = re.compile(
	r"\b(?:usdt|usdc|usdg|pyusd|dai|sol|solana|btc|bitcoin|eth|ethereum|stablecoin|crypto(?:currency)?)\b",
	re.I,
)
_BEGINNER = re.compile(r"\b(?:beginner|newbie|novice|entry[- ]level|first[- ]time|students?)\b", re.I)
_USD = re.compile(r"\$\s?([\d][\d,]*(?:\.\d+)?)\s?(k\b|m\b)?", re.I)
# "Join the X Challenge: $3,000 in Prizes Across 10 Winners" is an announcement;
# "Congrats to the X Winners" and the weekly roundups are not. The word
# "winners" appears in both, so the title has to *open* with the invitation.
_CHALLENGE_TITLE = re.compile(r"^\W*join (?:the|our|in)\b.*\b(?:challenge|hackathon|contest|competition)\b", re.I)
_MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def config() -> dict:
	"""Strategy config for this module. Read per call, never at import."""
	return load_config("research_feed", _DEFAULTS)


def _state(status: dict) -> dict:
	return status.setdefault("research_feed", {})


def _clip(value: Any, limit: int) -> str:
	text = re.sub(r"\s+", " ", str(value or "")).strip()
	return text if len(text) <= limit else text[: max(0, limit - 1)].rstrip() + "…"


def _get(url: str, params: Optional[dict] = None, timeout: tuple = (10, 40)) -> Any:
	"""Decoded JSON, or ``None`` on any failure (including a non-JSON challenge page)."""
	try:
		resp = requests.get(url, params=params, headers=_HEADERS, timeout=timeout)
		resp.raise_for_status()
		return resp.json()
	except Exception as exc:
		log.warning("[research_feed] %s failed: %s", url, exc)
		return None


def _usd(text: str) -> float:
	"""The largest dollar figure in ``text`` (``$1,000,000`` -> 1e6), or 0. Ranking only."""
	best = 0.0
	for number, unit in _USD.findall(text or ""):
		try:
			value = float(number.replace(",", ""))
		except ValueError:
			continue
		value *= 1_000 if unit.lower() == "k" else 1_000_000 if unit.lower() == "m" else 1
		best = max(best, value)
	return best


def _score(*, pays: bool, crypto: bool, kyc: str, beginner: bool, days_left: Optional[float], starts_in: float, size_usd: float) -> int:
	"""0-100. Stated prize, crypto, no KYC, newcomer friendly, then timing and size."""
	score = 30 if pays else 0
	score += 15 if crypto else 0
	score += 15 if kyc == "not required" else -15 if kyc == "required" else 0
	score += 10 if beginner else 0
	if starts_in > 0:
		# Not open yet: worth a look when it opens soon.
		score += 8 if starts_in <= 14 else 3
	elif days_left is None:
		score += 3
	else:
		# A row closing within a day cannot realistically be entered.
		score += 10 if days_left >= 2 else 4 if days_left >= 1 else 0
	# Size is graded so that rows tied on everything else still order by prize.
	score += 20 if size_usd >= 100_000 else 16 if size_usd >= 50_000 else 12 if size_usd >= 10_000 else 8 if size_usd >= 1_000 else 4 if size_usd >= 100 else 0
	return max(0, min(100, score))


def _row(
	source: str, ident: Any, category: str, title: str, url: str, cfg: dict, *,
	prize: str = "", detail: str = "", pays: bool = False, crypto: bool = False,
	kyc: str = "not published", deadline: Optional[datetime] = None,
	starts_at: Optional[datetime] = None, posted_at: Optional[datetime] = None,
	beginner: bool = False, size_usd: float = 0.0, now: datetime,
) -> dict:
	limit = int(cfg["text_max_chars"])
	days_left = None if deadline is None else (deadline - now).total_seconds() / 86400
	starts_in = 0.0 if starts_at is None else max(0.0, (starts_at - now).total_seconds() / 86400)
	return {
		"id": f"{source}:{ident}",
		"category": category,
		"source": source,
		"title": _clip(title, limit),
		"url": url,
		"prize": _clip(prize, 60),
		"detail": _clip(detail, limit),
		"pays": pays,
		"crypto": crypto,
		"kyc": kyc,
		"beginner": beginner,
		"deadline": deadline.isoformat(timespec="minutes") if deadline else None,
		"starts_at": starts_at.isoformat(timespec="minutes") if starts_at else None,
		"posted_at": posted_at.isoformat(timespec="minutes") if posted_at else None,
		"score": _score(
			pays=pays, crypto=crypto, kyc=kyc, beginner=beginner,
			days_left=days_left, starts_in=starts_in, size_usd=size_usd,
		),
	}


# ---------------------------------------------------------------- Devpost

def _devpost_range(text: Any) -> tuple[Optional[datetime], Optional[datetime]]:
	"""``"Oct 15 - Nov 05, 2026"`` / ``"Nov 04 - 11, 2026"`` -> (start, end) UTC, or (None, None).

	The end is taken as the end of its day, so a hackathon closing "today" is
	still listed until the day is over.
	"""
	parts = re.split(r"\s+-\s+", str(text or "").strip())
	if len(parts) != 2:
		return None, None
	right = re.fullmatch(r"(?:([A-Za-z]{3})[a-z]*\s+)?(\d{1,2}),\s*(\d{4})", parts[1].strip())
	left = re.fullmatch(r"([A-Za-z]{3})[a-z]*\s+(\d{1,2})(?:,\s*(\d{4}))?", parts[0].strip())
	if not right or not left:
		return None, None
	try:
		end_month = _MONTHS[(right.group(1) or left.group(1)).lower()]
		end_year = int(right.group(3))
		start_year = int(left.group(3) or end_year)
		start_month = _MONTHS[left.group(1).lower()]
		# "Dec 20 - Jan 10, 2027": the start belongs to the year before.
		if not left.group(3) and (start_month > end_month):
			start_year = end_year - 1
		start = datetime(start_year, start_month, int(left.group(2)), tzinfo=timezone.utc)
		end = datetime(end_year, end_month, int(right.group(2)), 23, 59, tzinfo=timezone.utc)
	except (KeyError, ValueError):
		return None, None
	return start, end


def fetch_devpost(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""Open and upcoming online hackathons, newest and biggest first, de-duplicated."""
	seen: dict[Any, dict] = {}
	got_any = False
	for order in ("recently-added", "prize-amount"):
		for page in range(1, max(1, int(cfg["devpost_pages"])) + 1):
			data = _get(
				"https://devpost.com/api/hackathons",
				{"status[]": ["open", "upcoming"], "challenge_type[]": "online", "order_by": order, "page": page, "per_page": 30},
			)
			batch = data.get("hackathons") if isinstance(data, dict) else None
			if not isinstance(batch, list):
				break
			got_any = True
			for item in batch:
				if isinstance(item, dict) and item.get("id") is not None:
					seen.setdefault(item["id"], item)
			if len(batch) < 30:
				break
	return list(seen.values()) if got_any else None


def build_devpost(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	if raw.get("invite_only") or raw.get("winners_announced") or str(raw.get("open_state") or "") not in ("open", "upcoming"):
		return None
	place = str((raw.get("displayed_location") or {}).get("location") or "").strip().lower()
	if place != "online":
		return None
	start, end = _devpost_range(raw.get("submission_period_dates"))
	if end is not None and end < now:
		return None
	if start is not None and (start - now) > timedelta(days=int(cfg["lookahead_days"])):
		return None
	# The feed wraps the figure in a <span>, which leaves "$ 1,000" after tag stripping.
	prize_text = re.sub(r"\$\s+", "$", strip_html(str(raw.get("prize_amount") or "")))
	size = _usd(prize_text)
	cash = int((raw.get("prizes_counts") or {}).get("cash") or 0) > 0
	pays = cash and size > 0
	themes = [str(t.get("name") or "") for t in raw.get("themes") or [] if isinstance(t, dict)]
	org = str(raw.get("organization_name") or "").strip()
	return _row(
		"devpost", raw.get("id"), "hackathon", str(raw.get("title") or ""), str(raw.get("url") or ""), cfg,
		prize=f"{prize_text} in prizes" if pays else "",
		detail=" · ".join(x for x in [org, ", ".join(themes[:2])] if x),
		pays=pays, beginner=any(_BEGINNER.search(t) for t in themes), size_usd=size,
		deadline=end, starts_at=start, now=now,
	)


# --------------------------------------------------------------- Superteam

def fetch_superteam(cfg: dict, now: datetime) -> Optional[list[dict]]:
	data = _get("https://superteam.fun/api/listings/", {"type": "bounty", "status": "open", "take": 50})
	return data if isinstance(data, list) else None


def build_superteam(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	deadline = parse_dt(raw.get("deadline"))
	if deadline is not None and deadline < now:
		return None
	if raw.get("isWinnersAnnounced") or str(raw.get("type") or "bounty") != "bounty":
		return None
	# "variable" pay is a freelance gig quoted per applicant: a job, not a prize.
	if str(raw.get("compensationType") or "fixed") == "variable":
		return None
	slug = str(raw.get("slug") or "").strip()
	amount = raw.get("rewardAmount")
	token = str(raw.get("token") or "").strip()
	if not slug or not isinstance(amount, (int, float)) or amount <= 0:
		return None
	sponsor = str((raw.get("sponsor") or {}).get("name") or "").strip()
	entries = (raw.get("_count") or {}).get("Submission")
	return _row(
		"superteam", slug, "crypto-bounty", str(raw.get("title") or ""),
		f"https://superteam.fun/earn/listing/{slug}", cfg,
		prize=f"{amount:,.0f} {token}".strip(),
		detail=" · ".join(x for x in [sponsor, f"{entries} entries" if isinstance(entries, int) else ""] if x),
		pays=True, crypto=True,
		# 1 stablecoin = 1 USD, so the size can rank; any other token is not priced.
		size_usd=float(amount) if token.upper() in {"USDC", "USDT", "USDG", "PYUSD", "DAI"} else 0.0,
		deadline=deadline, now=now,
	)


# ---------------------------------------------------------------- Immunefi

def fetch_immunefi(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""Every public program. The payload is ~6 MB of prose, so only a few fields are kept."""
	data = _get("https://immunefi.com/public-api/bounties.json", timeout=(10, 120))
	if not isinstance(data, list):
		return None
	keep = ("slug", "project", "maxBounty", "kyc", "launchDate", "endDate", "isPaused", "inviteOnly", "rewardsToken", "productType", "description")
	return [{k: item.get(k) for k in keep} for item in data if isinstance(item, dict)]


def build_immunefi(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	if raw.get("isPaused") or raw.get("inviteOnly"):
		return None
	slug, project = str(raw.get("slug") or "").strip(), str(raw.get("project") or "").strip()
	top = raw.get("maxBounty")
	if not slug or not project or not isinstance(top, (int, float)) or top <= 0:
		return None
	end = parse_dt(raw.get("endDate"))
	if end is not None and end < now:
		return None
	token = _clip(raw.get("rewardsToken"), 30)
	# A program that asks for KYC is one the owner cannot be paid by (doctrine
	# Principle 3h), so it is not listed: a row to open, read, and abandon.
	if raw.get("kyc") is True:
		return None
	kyc = "not required" if raw.get("kyc") is False else "not published"
	kinds = [str(k).replace("_", " ") for k in raw.get("productType") or [] if k][:2]
	return _row(
		"immunefi", slug, "bug-bounty", f"{project} bug bounty",
		f"https://immunefi.com/bug-bounty/{slug}/", cfg,
		prize=f"up to ${top:,.0f}" + (f" · {token}" if token else ""),
		detail=" · ".join(kinds) or _clip(raw.get("description"), 80),
		pays=True, crypto=bool(_CRYPTO.search(token)), kyc=kyc, size_usd=float(top),
		# `launchDate` is when the program went live. `updatedDate` changes
		# daily on old programs and would make every one look new.
		deadline=end, posted_at=parse_dt(raw.get("launchDate")), now=now,
	)


# ------------------------------------------------------- dev.to challenges

def fetch_challenges(cfg: dict, now: datetime) -> Optional[list[dict]]:
	data = _get("https://dev.to/api/articles", {"username": "devteam", "per_page": 50})
	return data if isinstance(data, list) else None


def build_challenge(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	"""DEV's own announcement of a challenge, never a submission to one."""
	path = str(raw.get("path") or "")
	title = str(raw.get("title") or "")
	if not path.startswith("/devteam/") or not _CHALLENGE_TITLE.search(title):
		return None
	posted = parse_dt(raw.get("published_timestamp"))
	if posted is None or (now - posted) > timedelta(days=int(cfg["challenge_max_age_days"])):
		return None
	text = f"{title} {raw.get('description') or ''}"
	size = _usd(text)
	return _row(
		"devto", raw.get("id"), "challenge", title, str(raw.get("url") or ""), cfg,
		prize=f"${size:,.0f} in prizes" if size else "", detail=_clip(raw.get("description"), 100),
		pays=size > 0, size_usd=size, posted_at=posted, now=now,
	)


# (source id, label, fetch, build)
SOURCES: list[tuple[str, str, Callable, Callable]] = [
	("devpost", "Devpost", fetch_devpost, build_devpost),
	("superteam", "Superteam Earn", fetch_superteam, build_superteam),
	("immunefi", "Immunefi", fetch_immunefi, build_immunefi),
	("devto", "DEV challenges", fetch_challenges, build_challenge),
]


# Beyond the shared table: wagering and speculative-token promotion. Superteam
# lists "Create Content on Premier League Predictions" and "Write a thread on
# $CHIMP Fair Launch" next to real bounties; neither is a row the owner should
# find on this page. Same rule as the shared table -- a false positive costs a
# row, a miss costs the page's credibility -- so nothing here is loosened to
# rescue one.
_RESEARCH_SCREEN = re.compile(
	r"\bpredictions?\b|\bprediction markets?\b|\bwager|\blotter(?:y|ies)\b|\bjackpot\b"
	r"|\bfair launch\b|\bpre-?sales?\b|\bmeme ?coins?\b|\bpump\.?fun\b|\bairdrop farm",
	re.I,
)


def screen(row: dict) -> str:
	"""The prohibited category of a row, or "". Reads everything a reader could see."""
	fields = (row.get("title"), row.get("detail"), row.get("prize"), row.get("url"))
	shared = prohibited_category(*fields)
	if shared:
		return shared
	return "wagering_or_token_promo" if _RESEARCH_SCREEN.search(" ".join(str(f or "") for f in fields)) else ""


def collect(raw_by_source: dict[str, Optional[list]], cfg: dict, now: datetime) -> tuple[list[dict], list[dict]]:
	"""Build, screen and de-duplicate rows. Returns ``(pool, source_stats)``.

	A source whose raw list is ``None`` contributes nothing here and is reported
	``ok: False``; the caller decides what to keep for it.
	"""
	pool: dict[str, dict] = {}
	stats = []
	for source, label, _fetch, build in SOURCES:
		raw = raw_by_source.get(source)
		entry = {"source": source, "label": label, "fetched": 0, "kept": 0, "screened": 0, "ok": raw is not None}
		for item in raw or []:
			entry["fetched"] += 1
			if not isinstance(item, dict):
				continue
			try:
				row = build(item, cfg, now)
			except Exception as exc:  # one malformed item must not cost the source
				log.warning("[research_feed] %s item skipped: %s", source, exc)
				continue
			if row is None:
				continue
			if screen(row):
				entry["screened"] += 1
				continue
			if row["id"] not in pool:
				pool[row["id"]] = row
				entry["kept"] += 1
		stats.append(entry)
	return list(pool.values()), stats


def select(pool: list[dict], cfg: dict, now: datetime) -> list[dict]:
	"""Cap each category with a reserved share for the newest rows, in category order."""
	out: list[dict] = []
	for category in CATEGORIES:
		rows = [r for r in pool if r["category"] == category]
		out.extend(select_fresh_first(
			rows, int(cfg["per_category_cap"]), now,
			fresh_share=float(cfg["min_fresh_share"]), fresh_hours=int(cfg["fresh_hours"]),
		))
	return out


def run(llm: Any = None, status: Optional[dict] = None) -> list[dict]:
	"""Refresh the feeds. ``llm`` is accepted and unused (see module docstring)."""
	status = status if isinstance(status, dict) else {}
	cfg = config()
	state = _state(status)
	action: dict[str, Any] = {"platform": "research-feed", "success": False, "estimated_usd": 0.0}

	if not cfg.get("enabled"):
		state["last_reason"] = "disabled"
		return []
	if hours_until_due(state, "last_refresh_at", int(cfg["refresh_hours"])) > 0:
		return []

	now = datetime.now(timezone.utc)
	previous_items = [r for r in state.get("items") or [] if isinstance(r, dict)]

	raw_by_source: dict[str, Optional[list]] = {}
	for source, _label, fetch, _build in SOURCES:
		try:
			raw_by_source[source] = fetch(cfg, now)
		except Exception as exc:
			log.warning("[research_feed] %s fetch crashed: %s", source, exc)
			raw_by_source[source] = None

	pool, stats = collect(raw_by_source, cfg, now)
	failed = [s["source"] for s in stats if not s["ok"]]
	if len(failed) == len(SOURCES):
		state["last_reason"] = "fetch_failed"
		action["error"] = "every research feed unreachable"
		return [action]

	# An unreadable source is not an empty one: its last good rows stay.
	have = {r["id"] for r in pool}
	for row in previous_items:
		if row.get("source") in failed and row.get("id") not in have:
			pool.append({k: v for k, v in row.items() if k != "discovered_at"})

	stamped, ledger = stamp_from_ledger(
		pool, state.get("first_seen"), lambda r: r.get("id", ""), now,
		seed=previous_items, seed_key=lambda r: r.get("id", ""),
		keep_days=int(cfg["ledger_days"]), max_entries=int(cfg["ledger_max_entries"]),
	)
	rows = select(stamped, cfg, now)

	state.update({
		"last_refresh_at": now.isoformat(),
		"last_reason": "ok" if not failed else "partial",
		"failed_sources": failed,
		"pool_total": len(stamped),
		"source_stats": stats,
		"first_seen": ledger,
		"items": rows,
	})
	action.update({"success": True, "listed": len(rows)})
	log.info("[research_feed] %d in pool, %d listed, failed: %s", len(stamped), len(rows), ", ".join(failed) or "none")
	return [action]
