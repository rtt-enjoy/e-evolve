"""
Shared primitives for the earning modules.

Every earning module needs the same four things: its slice of
``config/strategy.json``, a cadence check against a stored timestamp, and
tolerant parsers for the feed data it scrapes. Each module used to carry its
own copy, and the copies had drifted -- ``code_techs`` held a ``_parse_dt``
that could not read RFC-822 RSS dates and a ``_strip_html`` that left
``<script>`` bodies intact, while ``trending`` handled both. Consolidating on
the stronger implementation is what this module is for.

No module state and no I/O beyond reading the strategy file, so importing it
is free and it can be exercised directly in tests.
"""
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

CONFIG_FILE = Path("config/strategy.json")


# OWNER RULE (2026-11-03), top priority: nothing the bot lists may be adult,
# piracy, gambling, fraud or malware content. The table sits here, not in one
# product, because `code_techs` (Leads) and `research_feed` (Research) both
# fetch from open sources and must refuse the same things.

# Each pattern is one category. False positives are accepted on purpose: a
# legitimate repo that happens to say "keygen" is a lost row, while one
# prohibited row on the owner's dashboard is the failure this exists to stop.
# Do not loosen a pattern to rescue a row; add a narrower one only if a
# category starts emptying the page.
PROHIBITED_PATTERNS: dict[str, str] = {
	"adult": (
		r"porn|xxx|nsfw|hentai|onlyfans|\bsex(ual|y)?\b|\bnude|\bnudity\b|erotic|\bescorts?\b"
		r"|adult[- ](content|site|video|cam)s?|\bcamgirls?\b|\bfetish|\bxvideos\b|\bxhamster\b"
	),
	"piracy": (
		r"\bwarez\b|\bkeygens?\b|\bcrack(ed|s|ing)?\b|\bnulled\b|\bpirat(e|ed|es|ing|cy)\b"
		r"|\btorrents?\b|serial[- ]?keys?|licen[cs]e[- ]?keys?[- ]?(generator|gen)\b"
		r"|\bactivators?\b|\bkms[- ]?(pico|auto)\b|drm[- ]?(removal|remover|bypass|free)"
		r"|paywall[- ]?(bypass|remover)|bypass(es|ing)?[- ]paywalls?"
		r"|(youtube|netflix|spotify|tiktok|instagram|pornhub|onlyfans)[\w -]{0,20}(download|ripper)"
	),
	"gambling": r"\bcasinos?\b|gambl(e|ing)|\bbetting\b|sportsbook|\bslots? machine",
	# Trading is refused in code (Principle 6), so a trading bot is not a lead.
	"trading": r"trading[- ]bots?|\bmetatrader|\bmt[45]\b|\bforex\b|sniper[- ]bot|copy[- ]trad",
	"fraud": (
		r"fake[- ](id|ids|identity|documents?|passports?|reviews?)\b"
		r"|(driver'?s?|driving)[- ]licen[cs]e[- ]generator|\bcarding\b|\bcvv\b|\bphishing\b"
		r"|account[- ]generator|\bspam[- ]?bots?\b|\bmass[- ]dm\b|\bbotnet\b|\bddos\b"
		# Seen on a star-farmed `topic:developer-tools` listing: raiders, likers,
		# lock bypasses and "full working installer" cracked software.
		r"|\braiders?\b|\blikers?\b|boosting[- ]tools?|auto[- ]?(follow|like|view)\w*"
		r"|\b(ios|icloud|frp)[- ]?(unlock\w*|bypass)\b|full working installer"
	),
	"malware": (
		r"\bstealers?\b|\bkeyloggers?\b|\bransomware\b|\baimbot\b|\bwallhack\b"
		r"|game[- ]cheats?\b|cheat[- ](engine|menu|tool)s?\b"
	),
	"drugs_weapons": r"\bcannabis\b|\bmarijuana\b|\bdark ?web market|\bfirearms?\b|\bguns? (shop|store)\b",
}


def load_config(section: str, defaults: Mapping[str, Any] | None = None) -> dict:
	"""Return one section of the strategy file, with ``defaults`` filled in.

    Read at call time, never at import time. A module-level constant captured
    at import cannot see an owner's config edit without a reimport, and it
    forces tests to monkeypatch globals to change one setting.

    A missing or malformed file yields the defaults: bad config degrades the
    module to its documented behaviour rather than crashing the cycle.
    """
	try:
		raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get(section, {})
	except Exception:
		raw = {}
	cfg = dict(defaults or {})
	if isinstance(raw, dict):
		cfg.update(raw)
	return cfg


def hours_until_due(state: Mapping[str, Any], key: str, interval_hours: int) -> float:
	"""Hours remaining before ``key``'s cadence is due again. 0.0 when due now.

    A missing or unparseable stamp reads as due. A module that has never run
    must be allowed to run, and a corrupt timestamp must not wedge it forever.
    """
	stamp = str(state.get(key) or "").strip()
	if not stamp:
		return 0.0
	last = parse_dt(stamp)
	if last is None:
		return 0.0
	due = last + timedelta(hours=max(1, interval_hours))
	return max(0.0, (due - datetime.now(timezone.utc)).total_seconds() / 3600)


def parse_dt(value: Any) -> Optional[datetime]:
	"""Parse ISO-8601, RFC-822 (RSS ``pubDate``) or a unix epoch into aware UTC.

    Feeds serve all three, so all three are tried. A naive result is assumed
    UTC, which is what every source here publishes. The epoch branch exists
    because the remote-job APIs report ``pubDate`` as an integer, and without
    it a fresh posting reads as having no date at all.
    """
	if not value:
		return None
	raw = str(value).strip()
	# Epoch seconds. Bounded below so a bare year like "2026" cannot parse as
	# a timestamp in 1970, and above so milliseconds are not read as seconds.
	if re.fullmatch(r"\d{9,11}", raw):
		try:
			return datetime.fromtimestamp(int(raw), timezone.utc)
		except (OverflowError, OSError, ValueError):
			return None
	try:
		dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
		return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
	except Exception:
		pass
	try:
		from email.utils import parsedate_to_datetime
		dt = parsedate_to_datetime(raw)
		return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
	except Exception:
		return None


def strip_html(value: str) -> str:
	"""Flatten feed HTML to plain text.

    ``<script>`` bodies are dropped whole -- tag-stripping alone would leave
    the JavaScript source behind as if it were prose.

    Entities are *decoded*, not deleted. Replacing them with a space used to
    corrupt the text it was meant to clean: Hacker News serves "$120-160/hr"
    as ``$120-160&#x2F;hr``, so a rate a human actually typed came out as
    "$120-160 hr" and no downstream reader could recognise it as a price.
    Numeric entities were not matched at all, leaving raw ``&#x2F;`` in place.
    """
	value = re.sub(r"<script.*?</script>", " ", value, flags=re.DOTALL | re.IGNORECASE)
	value = re.sub(r"<[^>]+>", " ", value)
	value = html.unescape(value)
	return re.sub(r"\s+", " ", value).strip()


def xml_text(parent: ET.Element, tag: str) -> str:
	"""Text of the first ``tag`` child, namespace-agnostic. '' when absent."""
	element = parent.find(f"{{*}}{tag}")
	if element is None or element.text is None:
		return ""
	return element.text.strip()


def stamp_first_seen(items: Any, previous: Any, key: str, now: datetime) -> list:
	"""Give each dict in ``items`` a ``discovered_at``: when it first appeared.

    ``status.json`` is rewritten every refresh, so an item's own time cannot be
    read off the item. The stamp is carried over from ``previous`` (the last
    snapshot of the same list) by ``key``, and only an item the last snapshot
    did not hold is stamped ``now``. Without the carry-over every refresh would
    restamp every row and the page would say everything was added just now.
    Items with no ``key`` value are stamped ``now`` each time, because nothing
    can say they are the same item as before. Never raises.
    """
	seen: dict[str, str] = {}
	for old in previous if isinstance(previous, list) else []:
		if isinstance(old, dict) and old.get(key) not in (None, "") and old.get("discovered_at"):
			seen.setdefault(str(old[key]), str(old["discovered_at"]))
	stamp = now.isoformat()
	out = []
	for item in items if isinstance(items, list) else []:
		if isinstance(item, dict):
			item = {**item, "discovered_at": seen.get(str(item.get(key)), stamp) if item.get(key) not in (None, "") else stamp}
		out.append(item)
	return out


def bounded_append(entries: list, value: Any, limit: int) -> None:
	"""Append ``value`` if new, then trim ``entries`` to the newest ``limit``.

    Every history list in status.json is bounded this way so the file cannot
    grow without end across an hourly schedule.
    """
	if value and value not in entries:
		entries.append(value)
	del entries[: -max(1, limit)]


def prohibited_category(*parts: Any) -> str:
	"""The prohibited category the joined text falls in, or "" when it is allowed.

    Callers pass every field a reader could see -- title, tags, prize text, URL.
    A false positive costs one row; a miss puts prohibited content on the
    owner's page, so a pattern is never loosened to rescue a row.
    """
	text = " ".join(" ".join(str(x) for x in part) if isinstance(part, (list, tuple)) else str(part or "") for part in parts)
	for category, pattern in PROHIBITED_PATTERNS.items():
		if re.search(pattern, text, re.I):
			return category
	return ""


def stamp_from_ledger(
	items: Any,
	ledger: Any,
	key: Callable[[dict], str],
	now: datetime,
	*,
	seed: Any = None,
	seed_key: Optional[Callable[[dict], str]] = None,
	keep_days: int = 45,
	max_entries: int = 600,
) -> tuple[list, dict]:
	"""Stamp every item with ``discovered_at``: when this bot first saw it.

    ``stamp_first_seen`` carries a stamp over from the *previous displayed
    list*, so an item that a size cap drops and a later refresh brings back is
    restamped "just now" -- the page then claims a week-old row was added
    today. This reads a ledger of first sightings kept for the *whole pool*,
    cap or no cap, so a row keeps its stamp for as long as it is a candidate
    and for ``keep_days`` after it stops being one.

    ``seed`` (a previous snapshot's displayed rows, read with ``seed_key``)
    primes a ledger that does not exist yet, so a deploy does not reset every
    row to "just now". Returns ``(stamped items, new ledger)``. Never raises;
    an item with no usable key is stamped ``now`` and left out of the ledger.
    """
	stamp = now.isoformat(timespec="seconds")
	known: dict[str, str] = {}
	for old in (seed if isinstance(seed, list) else []):
		if isinstance(old, dict) and old.get("discovered_at"):
			k = (seed_key or key)(old)
			if k:
				known[str(k)] = str(old["discovered_at"])
	if isinstance(ledger, dict):
		known.update({str(k): str(v) for k, v in ledger.items() if v})

	out, current = [], {}
	for item in items if isinstance(items, list) else []:
		if not isinstance(item, dict):
			out.append(item)
			continue
		k = key(item)
		first = known.get(str(k), stamp) if k else stamp
		if k:
			current[str(k)] = first
		out.append({**item, "discovered_at": first})

	# Entries for rows that left the pool stay for `keep_days`, so a returning
	# row keeps its stamp; after that the ledger forgets them and stays bounded.
	cutoff = now - timedelta(days=max(1, keep_days))
	for k, v in known.items():
		if k not in current:
			when = parse_dt(v)
			if when is not None and when >= cutoff:
				current[k] = v
	if len(current) > max_entries:
		newest = sorted(current.items(), key=lambda kv: kv[1], reverse=True)[:max_entries]
		current = dict(newest)
	return out, current


def select_fresh_first(
	rows: list[dict],
	cap: int,
	now: datetime,
	*,
	fresh_share: float = 0.5,
	fresh_hours: int = 72,
	score_key: str = "score",
) -> list[dict]:
	"""Pick ``cap`` rows, reserving ``fresh_share`` of them for the newest.

    Ranking by score alone is how a page ends up identical from one day to the
    next: a row first seen this morning scores about what it will score next
    week, so the cap cuts it. Here the newest rows (``discovered_at`` within
    ``fresh_hours``, newest first) take their reserved slots *before* the score
    cut, and the remainder fills by score. ``fresh_share`` 0 reproduces a plain
    score ranking. Pure; rows are not copied or altered.
    """
	cap = max(0, int(cap))
	if cap == 0 or not rows:
		return []
	cutoff = now - timedelta(hours=max(1, fresh_hours))

	def listed(row: dict) -> Optional[datetime]:
		return parse_dt(row.get("discovered_at"))

	def by_score(row: dict) -> tuple:
		return (-int(row.get(score_key) or 0), str(row.get("title") or ""))

	chosen: list[dict] = []
	if fresh_share > 0:
		fresh = [r for r in rows if (listed(r) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff]
		# Newest sighting first; among rows seen in the same refresh, the one
		# the source itself dated latest, then the higher score.
		fresh.sort(key=lambda r: (str(r.get("discovered_at") or ""), str(r.get("posted_at") or ""), int(r.get(score_key) or 0)), reverse=True)
		chosen = fresh[: int(round(cap * min(1.0, fresh_share)))]
	taken = {id(r) for r in chosen}
	for row in sorted(rows, key=by_score):
		if len(chosen) >= cap:
			break
		if id(row) not in taken:
			chosen.append(row)
			taken.add(id(row))
	return sorted(chosen, key=by_score)
