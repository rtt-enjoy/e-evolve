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
- ``ai-free``       Free and cheap AI model APIs: permanent free tiers, renewable
                    credits, one-time trials (three maintained GitHub lists).
- ``ai-startup``    Startup credit programs for AI models and compute (four lists,
                    one of them the Sourcey JSON API). Owner directive 2026-11-16:
                    find as many as possible, startups first.

The two AI categories are **access, not prizes**: a row is a place to get model
calls cheaply, never money. They score on card needed, how long the free tier
lasts, and (for startups) how open the programme is. A programme that needs a
VC or accelerator is **listed and ranked down**, not dropped as Immunefi KYC
rows are, because the owner asked to see startup programmes and the
eligibility is printed on the row.

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
	# The two AI categories add ~300 candidates to a pool of ~150; a ledger that
	# is smaller than the pool restamps rows "just now" when it trims.
	"ledger_max_entries": 900,
	"text_max_chars": 110,
	# AI access rows are wider lists than prizes: the owner asked for as many as
	# can be found. Each row is ~0.5 KB in status.json.
	"ai_per_category_cap": 40,
	"ai_detail_chars": 170,
}

CATEGORIES: dict[str, str] = {
	"hackathon": "Hackathons",
	"crypto-bounty": "Crypto bounties",
	"bug-bounty": "Bug bounties",
	"challenge": "Dev challenges",
	"ai-startup": "AI credits for startups",
	"ai-free": "Free AI APIs",
}
AI_CATEGORIES = ("ai-startup", "ai-free")

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
	score: Optional[int] = None, extra: Optional[dict] = None,
) -> dict:
	limit = int(cfg["text_max_chars"])
	detail_limit = int(cfg.get("ai_detail_chars") or limit) if category in AI_CATEGORIES else limit
	days_left = None if deadline is None else (deadline - now).total_seconds() / 86400
	starts_in = 0.0 if starts_at is None else max(0.0, (starts_at - now).total_seconds() / 86400)
	return {
		"id": f"{source}:{ident}",
		"category": category,
		"source": source,
		"title": _clip(title, limit),
		"url": url,
		"prize": _clip(prize, 60),
		"detail": _clip(detail, detail_limit),
		"pays": pays,
		"crypto": crypto,
		"kyc": kyc,
		"beginner": beginner,
		"deadline": deadline.isoformat(timespec="minutes") if deadline else None,
		"starts_at": starts_at.isoformat(timespec="minutes") if starts_at else None,
		"posted_at": posted_at.isoformat(timespec="minutes") if posted_at else None,
		# `score` is for categories the prize formula does not describe (AI access).
		"score": score if score is not None else _score(
			pays=pays, crypto=crypto, kyc=kyc, beginner=beginner,
			days_left=days_left, starts_in=starts_in, size_usd=size_usd,
		),
		**(extra or {}),
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


# ------------------------------------------- AI access: free tiers, startup credits
#
# Seven keyless sources, none needing a key or an LLM. Six are maintained
# markdown lists on raw.githubusercontent.com (not api.github.com, whose
# anonymous quota of 60 an hour is shared with the leads page) and one is the
# Sourcey JSON API. A list is community-maintained and a claim, like a prize:
# every row links to the provider's own page and the owner reads the terms.
#
# A parser that finds nothing returns None, not []: a list that changes its
# table layout is an unreadable source, so its last good rows stay.

_RAW = "https://raw.githubusercontent.com/{repo}/HEAD/{path}"
_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_HTML_LINK = re.compile(r"""<a\s[^>]*href=["'](https?://[^"']+)["']""", re.I)
_TABLE_RULE = re.compile(r"^\|?[\s:|-]+\|?$")

# Reverse-engineered or ToS-evading endpoints turn up in free-LLM lists (a
# "reverse-engineered ChatGPT" proxy is a 900-star entry). The owner's top rule
# is no prohibited content, so these never reach the page. False positives cost
# a row; nothing here is loosened to rescue one.
_AI_SCREEN = re.compile(
	r"reverse[- ]?engineer|逆向|gpt4free|\bg4f\b|leaked (?:api )?keys?|shared (?:api )?keys?"
	r"|\bjailbreak|\buncensored\b|\bunrestricted\b|\bcracked\b|\bkey ?gen|\bproxy pool\b|\bfree-one-api\b",
	re.I,
)
_AI_AI = re.compile(r"\b(?:ai|a\.i\.|llm|llms|gpu|gpus|inference|openai|gemini|claude|bedrock|vertex|model|models|ml)\b", re.I)

_OPEN = re.compile(
	r"open to all|open to anyone|\bno vc\b|self-?serve|open application|\banyone\b|no funding|no investors?"
	r"|no application|no strings|bootstrapped|\bsolo\b|\bindie\b|\bfree to (?:join|apply)\b",
	re.I,
)
# Affiliation a solo company does not have. "raised under $10M" and "pre-Series B"
# are *ceilings* a small company passes, so they are deliberately not here.
_GATED = re.compile(
	r"\bvc\b|accelerator|incubator|portfolio|investors?\b|\bfunded\b|referral|invite|invitation"
	r"|backed by|venture-?backed|vc-?backed|membership|\bpartner network\b|via partner",
	re.I,
)
_NO_CARD = re.compile(r"no credit card|no card|without (?:a )?(?:credit )?card|card not required|\bno\b", re.I)
_PHONE = re.compile(r"phone|sms|verification", re.I)
_SIGNUP = re.compile(r"registration|sign[- ]?up|account", re.I)
_CARD = re.compile(r"credit card|card required|requires (?:a )?card|\bcard\b|payment method|billing|top[- ]?up", re.I)
_TRIAL = re.compile(r"\btrial\b|one[- ]time|sign-?up credits?|expires?", re.I)


def _get_text(url: str, timeout: tuple = (10, 40)) -> Optional[str]:
	"""Page text, or ``None`` on any failure."""
	try:
		resp = requests.get(url, headers=_HEADERS, timeout=timeout)
		resp.raise_for_status()
		return resp.text
	except Exception as exc:
		log.warning("[research_feed] %s failed: %s", url, exc)
		return None


def _plain(cell: Any) -> str:
	"""A markdown/HTML table cell as readable text."""
	text = _MD_LINK.sub(r"\1", str(cell or ""))
	text = re.sub(r"<[^>]+>", "", text).replace("**", "").replace("`", "")
	return re.sub(r"\s+", " ", text).strip()


def _split_row(line: str) -> list[str]:
	body = line.strip()
	body = body[1:] if body.startswith("|") else body
	body = body[:-1] if body.endswith("|") else body
	return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def _slug(text: str) -> str:
	return re.sub(r"[^a-z0-9]+", "-", str(text or "").lower()).strip("-")[:60]


def _md_tables(text: str) -> list[tuple[str, list[str], list[list[str]]]]:
	"""``(nearest heading, lower-cased headers, rows)`` for every pipe table outside code fences."""
	out: list[tuple[str, list[str], list[list[str]]]] = []
	lines = text.splitlines()
	section, fenced, i = "", False, 0
	while i < len(lines):
		line = lines[i].strip()
		if line.startswith("```"):
			fenced = not fenced
		elif fenced:
			pass
		elif re.match(r"#{1,6}\s", line):
			section = _plain(re.sub(r"^#+\s*", "", line))
		elif line.startswith("|") and i + 1 < len(lines) and "-" in lines[i + 1] and _TABLE_RULE.match(lines[i + 1].strip()):
			headers = [_plain(c).lower().rstrip("?").strip() for c in _split_row(line)]
			rows: list[list[str]] = []
			i += 2
			while i < len(lines) and lines[i].strip().startswith("|"):
				rows.append(_split_row(lines[i]))
				i += 1
			out.append((section, headers, rows))
			continue
		i += 1
	return out


def _table_items(text: str, *, sections: str = "", first: tuple = ("program", "provider"), need: str = "") -> list[dict]:
	"""One dict per table row, keyed by lower-cased header, plus ``section``, ``name`` and ``url``.

	``sections`` is a regex on the heading above the table; ``first`` the allowed
	first-column headers; ``need`` a header every accepted table must also have.
	"""
	items: list[dict] = []
	for section, headers, rows in _md_tables(text):
		if not headers or headers[0] not in first or (need and need not in headers):
			continue
		if sections and not re.search(sections, section, re.I):
			continue
		for cells in rows:
			if not cells or not _plain(cells[0]):
				continue
			item: dict[str, Any] = {h: cells[n] if n < len(cells) else "" for n, h in enumerate(headers)}
			link = _MD_LINK.search(cells[0])
			url = link.group(2) if link else ""
			if not url:
				anchor = next((m.group(1) for c in cells for m in [_HTML_LINK.search(c)] if m), "")
				url = anchor
			item.update({"section": section, "name": _plain(cells[0]), "url": url})
			items.append(item)
	return items


def _host_key(url: str) -> str:
	"""``aistudio.google.com`` -> ``google``: the registrable label, to merge one provider listed twice."""
	host = re.sub(r"^https?://", "", str(url or "")).split("/")[0].split(":")[0].lower().split(".")
	return host[-2] if len(host) >= 2 else ""


def _card(text: str) -> str:
	"""``none`` / ``signup`` / ``phone`` / ``card`` / ``unstated`` from a "credit card?" cell or prose."""
	value = _plain(text)
	if not value or value in ("-", "—", "?"):
		return "unstated"
	if re.search(r"credit card|card required|requires (?:a )?card|\bcard\b|top[- ]?up", value, re.I) and not re.search(r"\bno\b.{0,12}card|without.{0,8}card", value, re.I):
		return "card"
	if _PHONE.search(value):
		return "phone"
	if _SIGNUP.search(value):
		return "signup"
	if _NO_CARD.search(value):
		return "none"
	return "unstated"


def _eligibility(text: str) -> str:
	"""``open`` / ``conditions`` / ``gated`` / ``unstated``. Open wins: a self-serve tier is an entry point."""
	value = _plain(text)
	if not value or value in ("-", "—"):
		return "unstated"
	if _OPEN.search(value):
		return "open"
	if _GATED.search(value):
		return "gated"
	return "conditions"


def _ai_score(*, category: str, card: str, tier: str, eligibility: str, size_usd: float, kind: str = "") -> int:
	"""0-100 for a row that is access, not a prize.

	Free APIs: no card beats a plain signup beats a phone check beats a card; a permanent free tier
	beats renewable credit beats a one-time trial. Startup programmes: how open
	they are to a solo company first, then what is handed over (credit or a free
	service beats a discount), then size. Rate limits are display only.
	"""
	score = 20
	score += {"none": 25, "signup": 15, "phone": 10, "card": -10}.get(card, 0)
	score += {"permanent": 25, "renewable": 15, "trial": 8}.get(tier, 0)
	if category == "ai-startup":
		score += {"open": 20, "conditions": 8, "gated": -8}.get(eligibility, 0)
		score += {"credit": 12, "free-service": 12, "discount": 4}.get(kind, 0)
		score += 14 if size_usd >= 50_000 else 10 if size_usd >= 10_000 else 6 if size_usd >= 1_000 else 3 if size_usd >= 100 else 0
	return max(0, min(100, score))


def _ai_row(
	source: str, ident: Any, category: str, title: str, url: str, cfg: dict, *, prize: str, detail: str,
	card: str = "unstated", tier: str = "", eligibility: str = "unstated", kind: str = "",
	posted_at: Optional[datetime] = None, now: datetime,
) -> dict:
	size = _usd(prize)
	return _row(
		source, ident, category, title, url, cfg, prize=prize, detail=detail, posted_at=posted_at,
		size_usd=size, now=now,
		score=_ai_score(category=category, card=card, tier=tier, eligibility=eligibility, size_usd=size, kind=kind),
		extra={"card": card, "tier": tier, "eligibility": eligibility},
	)


# --- free AI APIs ------------------------------------------------------------

_TIER_PRIZE = {"permanent": "permanent free tier", "renewable": "renewable free credits", "trial": "one-time trial credits"}


def fetch_freellm_directory(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""nejib1/Free-LLM: permanent, renewable and trial tables with a card column."""
	text = _get_text(_RAW.format(repo="nejib1/Free-LLM", path="README.md"))
	if text is None:
		return None
	return _table_items(text, sections=r"permanent|renewable|trial", need="credit card") or None


def build_freellm_directory(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	section = str(raw.get("section") or "").lower()
	tier = "permanent" if "permanent" in section else "renewable" if "renewable" in section else "trial"
	name, url = str(raw.get("name") or ""), str(raw.get("url") or "")
	if not name or not url:
		return None
	prize = _TIER_PRIZE[tier]
	if tier == "trial" and _plain(raw.get("credit amount")):
		prize = f"{_plain(raw.get('credit amount'))} trial credits"
	elif tier == "renewable" and _plain(raw.get("free offer")):
		prize = _plain(raw.get("free offer"))
	limit = _plain(raw.get("rate limit"))
	models = _plain(raw.get("key models"))
	return _ai_row(
		"freellm-dir", _slug(name), "ai-free", name, url, cfg, prize=prize,
		detail=" · ".join(x for x in [models, limit] if x and x not in ("-", "—")),
		card=_card(raw.get("credit card")), tier=tier, now=now,
	)


def fetch_freellm_net(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""open-free-llm-api/awesome-freellm-apis: free-model counts and key links, refreshed daily upstream."""
	text = _get_text(_RAW.format(repo="open-free-llm-api/awesome-freellm-apis", path="README.md"))
	if text is None:
		return None
	return _table_items(text, need="free models") or None


def build_freellm_net(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	name = str(raw.get("name") or "")
	url = str(raw.get("url") or "")
	if not name or not url:
		return None
	renewable = "credit model" in raw
	count = _plain(raw.get("free models"))
	prize = _plain(raw.get("credit model")) if renewable else (f"{count} free models" if count else "free tier")
	detail = " · ".join(x for x in [f"context {_plain(raw.get('max context'))}" if _plain(raw.get("max context")) else "", _plain(raw.get("modalities"))] if x)
	return _ai_row(
		"freellm-net", _slug(name), "ai-free", name, url, cfg, prize=prize, detail=detail,
		card=_card(raw.get("credit card")), tier="renewable" if renewable else "permanent", now=now,
	)


_MNFST_HEAD = re.compile(r"^###\s+\[([^\]]+)\]\((https?://[^)\s]+)\)")


def fetch_mnfst(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""mnfst/awesome-free-llm-apis: one ``### [Provider](key page)`` heading and a sentence on the tier."""
	text = _get_text(_RAW.format(repo="mnfst/awesome-free-llm-apis", path="README.md"))
	if text is None:
		return None
	items: list[dict] = []
	lines = text.splitlines()
	for n, line in enumerate(lines):
		head = _MNFST_HEAD.match(line.strip())
		if not head:
			continue
		body = ""
		for nxt in lines[n + 1 : n + 8]:
			clean = nxt.strip()
			if clean and not clean.startswith(("|", "#", "<", "Base URL", "Native", "OpenAI-compatible")):
				body = clean
				break
		items.append({"name": head.group(1).strip(), "url": head.group(2), "body": _plain(body)})
	return items or None


def build_mnfst(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	name, url = str(raw.get("name") or ""), str(raw.get("url") or "")
	body = str(raw.get("body") or "")
	if not name or not url:
		return None
	tier = "trial" if _TRIAL.search(body) and not re.search(r"permanent|free tier|forever|ongoing", body, re.I) else "permanent"
	return _ai_row(
		"mnfst", _slug(name), "ai-free", name, url, cfg, prize=_TIER_PRIZE[tier], detail=body,
		card="none" if re.search(r"no credit card|no card", body, re.I) else "card" if _CARD.search(body) else "unstated",
		tier=tier, now=now,
	)


# --- startup credit programmes -----------------------------------------------

def _startup_row(source: str, raw: dict, cfg: dict, now: datetime, *, prize: str, detail: str, eligibility_text: str, eligibility: str = "") -> Optional[dict]:
	name, url = str(raw.get("name") or ""), str(raw.get("url") or "")
	if not name or not url or not prize:
		return None
	elig = eligibility or _eligibility(eligibility_text)
	shown = _plain(eligibility_text)
	return _ai_row(
		source, _slug(name), "ai-startup", name, url, cfg, prize=prize,
		detail=" · ".join(x for x in [f"for: {shown}" if shown and shown not in ("-", "—") else "", detail] if x),
		eligibility=elig, now=now,
	)


def fetch_bootstrapped(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""aidenixai/bootstrapped-credits: what a company with no VC actually gets, with when it was checked."""
	text = _get_text(_RAW.format(repo="aidenixai/bootstrapped-credits", path="README.md"))
	return None if text is None else (_table_items(text, first=("program",)) or None)


def build_bootstrapped(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	prize = _plain(raw.get("bootstrapped gets") or raw.get("what you get"))
	models = [f"{label}: {_plain(raw.get(key))}" for key, label in (("claude", "Claude"), ("gpt", "GPT"), ("open models", "open models")) if _plain(raw.get(key))]
	note = _plain(raw.get("catch") or raw.get("notes"))
	expires = _plain(raw.get("expires"))
	checked = _plain(raw.get("checked"))
	detail = " · ".join(x for x in [", ".join(models), f"expires {expires}" if expires else "", note, f"checked {checked}" if checked else ""] if x)
	# The whole list is written for a company with no investor, so a row is open
	# to this owner unless its own text says otherwise; "no application" rows need only a signup.
	no_application = "no application" in str(raw.get("section") or "").lower()
	return _startup_row(
		"bootstrapped", raw, cfg, now, prize=prize, detail=detail,
		eligibility_text="" if no_application else "a registered company with a live website",
		eligibility="open" if no_application else "conditions",
	)


def fetch_builders(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""doanbactam/awesome-builder-programs: official programme pages only; startups and AI credits."""
	text = _get_text(_RAW.format(repo="doanbactam/awesome-builder-programs", path="README.md"))
	return None if text is None else (_table_items(text, sections=r"startups|ai and developer credits", first=("program",)) or None)


def build_builders(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	benefit = _plain(raw.get("benefit"))
	provider = _plain(raw.get("provider"))
	return _startup_row("builders", raw, cfg, now, prize=benefit, detail=provider, eligibility_text=benefit)


def fetch_startup_credits_list(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""avinash201199/awesome-startup-credits: the cloud and AI/ML tables, with an eligibility column."""
	text = _get_text(_RAW.format(repo="avinash201199/awesome-startup-credits", path="README.md"))
	return None if text is None else (_table_items(text, sections=r"cloud infrastructure|ai\s*/\s*ml", first=("program",)) or None)


def build_startup_credits_list(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	prize = _plain(raw.get("credits (up to)") or raw.get("offer") or raw.get("what it unlocks"))
	return _startup_row(
		"startup-credits", raw, cfg, now, prize=prize, detail=_plain(raw.get("notes")),
		eligibility_text=_plain(raw.get("eligibility")),
	)


def _statements(rule: Any) -> list[str]:
	"""Every human-readable ``statement`` in a Sourcey eligibility tree."""
	out: list[str] = []
	if isinstance(rule, dict):
		if isinstance(rule.get("statement"), str):
			out.append(rule["statement"])
		for value in rule.values():
			out.extend(_statements(value))
	elif isinstance(rule, list):
		for value in rule:
			out.extend(_statements(value))
	return out


def fetch_sourcey(cfg: dict, now: datetime) -> Optional[list[dict]]:
	"""Sourcey's startup-credit catalogue: AI/ML entities plus AI-relevant hosting. Public offers only."""
	items: list[dict] = []
	got_any = False
	for category in ("ai-ml", "hosting-infra"):
		data = _get("https://api.sourcey.com/v1/entities", {"category": category, "limit": 100}, timeout=(10, 60))
		batch = data.get("data") if isinstance(data, dict) else None
		if not isinstance(batch, list):
			continue
		got_any = True
		for entity in batch:
			if not isinstance(entity, dict):
				continue
			programs = {p.get("program_id"): p for p in entity.get("programs") or [] if isinstance(p, dict)}
			for offer in entity.get("offers") or []:
				if not isinstance(offer, dict):
					continue
				access = offer.get("access") or {}
				benefits = (offer.get("economics") or {}).get("benefits") or []
				program = programs.get(offer.get("program_id")) or {}
				items.append({
					"entity": entity.get("name"), "category": category, "website": entity.get("website"),
					"title": offer.get("title"), "summary": offer.get("summary") or program.get("summary"),
					"lifecycle": offer.get("lifecycle"), "availability": access.get("availability"),
					"url": access.get("url") or entity.get("website"), "effective_from": offer.get("effective_from"),
					"kind": (benefits[0].get("kind") if benefits and isinstance(benefits[0], dict) else ""),
					"eligibility": " ".join(_statements((offer.get("eligibility") or {}).get("rule")))[:400],
					"id": offer.get("offer_id") or offer.get("slug"),
				})
	return items if got_any else None


def build_sourcey(raw: dict, cfg: dict, now: datetime) -> Optional[dict]:
	if raw.get("lifecycle") != "active" or raw.get("availability") not in (None, "public"):
		return None
	entity, title, summary = str(raw.get("entity") or ""), str(raw.get("title") or ""), str(raw.get("summary") or "")
	# Hosting is mostly not AI: keep it when the offer or the company is.
	if raw.get("category") == "hosting-infra" and not _AI_AI.search(f"{entity} {title} {summary}"):
		return None
	if not entity or not title or not raw.get("url") or not raw.get("id"):
		return None
	return _ai_row(
		"sourcey", _slug(raw["id"]), "ai-startup", entity, str(raw["url"]), cfg, prize=title,
		detail=" · ".join(x for x in [f"for: {_clip(raw.get('eligibility'), 90)}" if raw.get("eligibility") else "", _clip(summary, 90)] if x),
		eligibility=_eligibility(str(raw.get("eligibility") or "")), kind=str(raw.get("kind") or ""),
		posted_at=parse_dt(raw.get("effective_from")), now=now,
	)


# (source id, label, fetch, build). Order is priority when two sources list the
# same provider: the first one listed keeps the row.
SOURCES: list[tuple[str, str, Callable, Callable]] = [
	("devpost", "Devpost", fetch_devpost, build_devpost),
	("superteam", "Superteam Earn", fetch_superteam, build_superteam),
	("immunefi", "Immunefi", fetch_immunefi, build_immunefi),
	("devto", "DEV challenges", fetch_challenges, build_challenge),
	("bootstrapped", "Bootstrapped credits", fetch_bootstrapped, build_bootstrapped),
	("builders", "Builder programs", fetch_builders, build_builders),
	("startup-credits", "Startup credits list", fetch_startup_credits_list, build_startup_credits_list),
	("sourcey", "Sourcey", fetch_sourcey, build_sourcey),
	("freellm-dir", "Free-LLM directory", fetch_freellm_directory, build_freellm_directory),
	("freellm-net", "FreeLLM", fetch_freellm_net, build_freellm_net),
	("mnfst", "Awesome free LLM APIs", fetch_mnfst, build_mnfst),
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
	text = " ".join(str(f or "") for f in fields)
	if _RESEARCH_SCREEN.search(text):
		return "wagering_or_token_promo"
	return "ai_access_abuse" if row.get("category") in AI_CATEGORIES and _AI_SCREEN.search(text) else ""


_NOISE = re.compile(r"\([^)]*\)|\b(?:startups?|programs?|programmes?|for|credits?|founders?|hub|the|ai|api|apis)\b", re.I)


def _same_row_keys(row: dict) -> set[str]:
	"""Names that mean "the same offer" inside one AI category: the title, and for free APIs the host.

	``aistudio.google.com`` is one free tier whichever list names it; Google's
	*startup* programmes share a host and are different offers, so hosts only
	merge free-API rows.
	"""
	name = re.sub(r"[^a-z0-9]+", "", _NOISE.sub(" ", str(row.get("title") or "").lower()))
	keys = {f"name:{name}"} if name else set()
	if row.get("category") == "ai-free" and _host_key(row.get("url", "")):
		keys.add(f"host:{_host_key(row['url'])}")
	return keys


def collect(raw_by_source: dict[str, Optional[list]], cfg: dict, now: datetime) -> tuple[list[dict], list[dict]]:
	"""Build, screen and de-duplicate rows. Returns ``(pool, source_stats)``.

	A source whose raw list is ``None`` contributes nothing here and is reported
	``ok: False``; the caller decides what to keep for it. The same AI offer
	listed by two sources keeps the one from the earlier source in ``SOURCES``.
	"""
	pool: dict[str, dict] = {}
	seen: set[tuple[str, str]] = set()
	stats = []
	for source, label, _fetch, build in SOURCES:
		raw = raw_by_source.get(source)
		entry = {"source": source, "label": label, "fetched": 0, "kept": 0, "screened": 0, "duplicates": 0, "ok": raw is not None}
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
			if row["id"] in pool:
				continue
			keys = {(row["category"], k) for k in _same_row_keys(row)} if row["category"] in AI_CATEGORIES else set()
			if keys & seen:
				entry["duplicates"] += 1
				continue
			seen |= keys
			pool[row["id"]] = row
			entry["kept"] += 1
		stats.append(entry)
	return list(pool.values()), stats


def select(pool: list[dict], cfg: dict, now: datetime) -> list[dict]:
	"""Cap each category with a reserved share for the newest rows, in category order."""
	out: list[dict] = []
	for category in CATEGORIES:
		rows = [r for r in pool if r["category"] == category]
		cap = cfg.get("ai_per_category_cap") if category in AI_CATEGORIES else None
		out.extend(select_fresh_first(
			rows, int(cap or cfg["per_category_cap"]), now,
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
