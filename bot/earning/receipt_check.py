"""
Independent verification that published posts actually carry the ask.

Every other signal about the receive path is the bot grading its own homework.
``backfill`` computes ``remaining`` from the same ``fetch_published`` call it
acts on, so when that call returned wrong data the work and the claim about the
work were wrong *together*, and agreed with each other. ``payout.live`` reports
config, not reality. ``updated_total`` counts write attempts this process made,
not footers a reader can see.

That is not hypothetical. Between cycles #1760 and #1773 ``status["backfill"]``
read ``remaining: 0, last_reason: "nothing_to_do"`` -- by the doctrine's own
checklist, "every reader can pay" -- while not one of the account's 11 published
posts carried a footer, including the 1,722-view article holding 84% of all
lifetime reach. The failure was invisible for fourteen cycles because nothing
ever looked at a published post.

The doctrine's answer (Principle 3d) is to go and look::

    curl -s "https://dev.to/api/articles/<user>/<slug>" | grep -c "Support this work"

That is exactly right, and as a *manual* step in an unattended hourly system it
is a step that never happens. This module is that curl, run every cycle.

**It observes from outside.** ``GET /api/articles/{id}`` is unauthenticated and
returns ``body_markdown``, so this reads what any reader sees rather than what
the account's own authenticated view reports. It shares no serializer and no API
key with the write it checks, which is the entire point: a verifier that reuses
the writer's data can only ever confirm the writer's mistakes. Verified against
Forem's ``me.json.jbuilder`` and the public article-list partial -- the two
differ in exactly the field that caused the outage.

Scored against Principle 2 it needs no new secret (it needs no key at all), no
owner action, and no policy change, and it turns an asserted truth into a
verified one.

**It never writes to dev.to and never repairs anything.** Repair belongs to
``backfill``; merging them would rebuild the same problem one layer up, with the
fixer again reporting on itself. The only output here is an observation, and its
most valuable result is the one that contradicts the rest of ``status.json``.

**It covers the catalogue, not a fixed sample.** This module acquired a narrower
version of the bug it exists to catch. ``verify`` read ``max_per_cycle`` posts
sorted by views, with no rotation and no memory -- so with 13 published posts and
a cap of 5 it was not five posts per cycle on a rolling basis, it was *the same
five posts every cycle* and eight that could not be observed in any cycle, while
``last_reason`` reported ``all_verified``. Measured at cycle #1791:
``checked: 5`` beside an account of 13.

An independent fetch of all 13 confirmed they genuinely carried the ask, so the
answer was correct -- which is the more dangerous failure, because a right answer
from a method that could not have detected the error is never revisited.

So the cap stays (it is what keeps this cheap and rate-limit-safe) and gains a
denominator:

- The **busiest post is re-checked every cycle**. The view distribution is
  top-heavy enough that a footer silently lost from the evergreen post outweighs
  the rest of the catalogue combined.
- The **remaining slots go to the least-recently-verified**, so every post is
  reached within ``ceil(n / max_per_cycle)`` cycles rather than never.
- The **verdict is stored per post**, not just the timestamp. A gap found in one
  cycle is not in the next cycle's sample, and a module judging on
  ``without_footer`` alone would flag it, rotate on, and report ``all_verified``
  one cycle later -- erasing the finding with the mechanism that produced it.
- An **observation expires** (``stale_after_hours``), because a post read once is
  evidence about the day it was read.

Read ``covered`` / ``published_total`` and ``known_without_footer``. ``checked``
and ``without_footer`` describe this cycle's sample only.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import requests

from . import _shared, payout

log = logging.getLogger(__name__)

# Unauthenticated on purpose. Sending the api-key here would read the article
# through the authenticated serializer -- the same view the backfill already
# trusts -- and re-introduce the shared blind spot this module exists to avoid.
_API = "https://dev.to/api/articles/{id}"
_TIMEOUT = 20

DEFAULTS: dict[str, Any] = {
	"enabled": True,
	# Posts verified per cycle, highest-traffic first. The view distribution is
	# top-heavy enough that a handful of posts is most of the answer, and this
	# stays well clear of any rate limit on an hourly schedule.
	"max_per_cycle": 5,
	# How long one observation stays evidence. A post read once and never again
	# says what was true that day; a footer can be lost to a hand-edit at any
	# time. Past this, the post re-enters the rotation and stops counting as
	# covered. 0 disables expiry (a verification then never goes stale).
	"stale_after_hours": 168,
	"history_limit": 50,
}


def config() -> dict[str, Any]:
	"""This module's slice of config/strategy.json, read at call time."""
	return _shared.load_config("receipt_check", DEFAULTS)


def _state(status: dict) -> dict:
	return status.setdefault("receipt_check", {
		"checked": 0,
		"with_footer": 0,
		"without_footer": 0,
		"unreachable": 0,
		"missing": [],
		"last_run": None,
		"last_reason": None,
		"agrees_with_backfill": None,
		# Coverage, tracked across cycles. `checked` counts this cycle's sample;
		# these count the catalogue. See _coverage for why the distinction is
		# load-bearing rather than cosmetic.
		"published_total": 0,
		"verified_ids": [],
		"covered": 0,
		"unverified": 0,
		"coverage_complete": None,
		"oldest_check_age_hours": None,
	})


def fetch_live_body(article_id: int, timeout: int = _TIMEOUT) -> Optional[str]:
	"""Return the published body of one article as any reader sees it.

    ``None`` means "could not observe", which is deliberately distinct from
    ``""`` meaning "observed, and empty". Conflating those is how the original
    bug hid: an unreadable body was read as a body with nothing wrong in it.
    """
	try:
		resp = requests.get(
			_API.format(id=int(article_id)),
			headers={"Accept": "application/vnd.forem.api-v1+json"},
			timeout=timeout,
		)
		resp.raise_for_status()
		data = resp.json()
	except Exception as exc:
		log.debug("[receipt_check] fetch %s failed: %s", article_id, exc)
		return None

	if not isinstance(data, dict):
		return None
	body = data.get("body_markdown")
	# A response that omits the field entirely is an observation failure, not an
	# article without a footer. Reporting it as the latter would raise a false
	# alarm on every post the moment a serializer changes again -- the mirror
	# image of the bug this module exists to catch.
	if body is None:
		return None
	return str(body)


def select(posts: list[dict[str, Any]], limit: int = 5,
		   last_seen: dict[Any, str] | None = None) -> list[dict[str, Any]]:
	"""Choose which posts to observe this cycle: busiest first, then oldest read.

    A per-cycle cap makes this a *sample*, and a sample that is always the same
    five posts is not a rolling verification -- it is five verified posts and a
    permanent blind spot wearing the word "all". Sorting by views alone did
    exactly that: with 13 published posts and ``max_per_cycle: 5``, posts ranked
    6-13 could never be observed, in any cycle, ever, while ``last_reason`` read
    ``all_verified``. That is Principle 3d's completion-signal-from-a-guard, one
    layer up: the cap is correct, and reporting the capped result as coverage is
    not.

    So the budget is split. The busiest post is most of the reach and must be
    re-checked every cycle -- a footer silently lost from it outweighs the rest
    of the catalogue combined, and `test_highest_traffic_first` pins that. The
    remaining slots go to whatever was verified longest ago, so every post is
    reached within ``ceil(n / limit)`` cycles instead of never.
    """
	seen = last_seen or {}
	ranked = sorted(
		(p for p in posts if p.get("id") is not None),
		key=lambda p: int(p.get("page_views") or 0),
		reverse=True,
	)
	budget = max(1, int(limit))
	if not ranked:
		return []

	# Slot one: the busiest post, unconditionally.
	chosen = [ranked[0]]
	rest = ranked[1:]

	# Remaining slots: least-recently-verified first. A post never seen sorts
	# ahead of every post that has been, because "never observed" is the state
	# this function exists to drain. Views break ties, so within a cohort of
	# equally-stale posts the busiest still goes first.
	rest.sort(key=lambda p: (
		str(seen.get(p.get("id")) or ""),
		-int(p.get("page_views") or 0),
	))
	chosen.extend(rest[:budget - 1])
	return chosen


def verify(posts: list[dict[str, Any]], cfg: dict[str, Any] | None = None,
		   limit: int = 5,
		   last_seen: dict[Any, str] | None = None) -> dict[str, Any]:
	"""Check a rotating sample of published posts for a reader-visible ask.

    Takes the post list only for ids and view counts -- the body is always
    re-fetched from the public endpoint, never read from the caller's data.
    That separation is the whole value of this function.
    """
	payout_cfg = cfg or payout.config()
	ranked = select(posts, limit, last_seen)

	result: dict[str, Any] = {
		"checked": 0, "with_footer": 0, "without_footer": 0,
		"unreachable": 0, "missing": [],
		# What was actually observed this cycle, as ``{id: bool has_footer}``.
		# An unreachable post is deliberately absent: it was not verified, so
		# ageing it as if it had been would let a permanently-404ing post drift
		# out of the rotation and quietly stop being asked about.
		"observed": {},
	}

	for post in ranked:
		body = fetch_live_body(int(post["id"]))
		if body is None:
			result["unreachable"] += 1
			continue
		result["checked"] += 1
		ok = payout.has_footer(body, payout_cfg)
		result["observed"][post.get("id")] = ok
		if ok:
			result["with_footer"] += 1
		else:
			result["without_footer"] += 1
			result["missing"].append({
				"id": post.get("id"),
				"title": str(post.get("title") or "")[:80],
				"views": int(post.get("page_views") or 0),
				"url": str(post.get("url") or ""),
			})
	return result


def _ledger(state: dict) -> dict[Any, dict]:
	"""``{article_id: {"at": iso timestamp, "ok": had a footer}}``.

    The verdict is stored, not just the timestamp, because the rotation moves
    on. A post found footerless in one cycle is not in the next cycle's sample,
    so a module that remembered only *when* it looked would report
    ``all_verified`` one cycle after finding a real gap -- erasing the finding
    with the rotation that produced it.
    """
	out: dict[Any, dict] = {}
	for row in state.get("verified_ids") or []:
		if isinstance(row, dict) and row.get("id") is not None:
			out[row["id"]] = {"at": str(row.get("at") or ""),
							  "ok": bool(row.get("ok", True))}
	return out


def _seen_map(state: dict) -> dict[Any, str]:
	"""``{article_id: iso timestamp of last successful observation}``."""
	return {k: v["at"] for k, v in _ledger(state).items()}


def _record_seen(state: dict, observed: dict, now: datetime,
				 posts: list[dict[str, Any]], limit: int) -> None:
	"""Stamp the posts observed this cycle and forget ones no longer published.

    Only *observed* ids are stamped -- an unreachable post keeps its old
    timestamp (or none at all) so it stays at the front of the rotation instead
    of being aged as though it had been read. That is the same third-state
    discipline `fetch_live_body` applies to a single post, held across cycles.

    Ids that are no longer in the published list are dropped, so a deleted post
    cannot sit in the ledger inflating `covered` forever.
    """
	live = {p.get("id") for p in posts if p.get("id") is not None}
	stamp = now.isoformat()
	seen = _ledger(state)
	for art_id, ok in (observed or {}).items():
		if art_id is not None:
			seen[art_id] = {"at": stamp, "ok": bool(ok)}
	rows = [{"id": k, "at": v["at"], "ok": v["ok"]}
			for k, v in seen.items() if k in live]
	# Freshest last, so the trim below drops the stalest entries first.
	rows.sort(key=lambda r: str(r["at"] or ""))
	state["verified_ids"] = rows[-max(1, int(limit)):]


def _coverage(state: dict, posts: list[dict[str, Any]],
			  now: datetime) -> dict[str, Any]:
	"""How much of the published catalogue this module has actually observed.

    ``checked`` answers "how many posts did I read this cycle". It was being
    read as "how many posts are fine", which are different questions whenever
    ``max_per_cycle`` is smaller than the catalogue -- and it always is, by
    design. These fields answer the second question.

    A verification also expires. A post read once and never again is evidence
    about the day it was read, not about today, and a footer can be lost to a
    hand-edit at any time. So an observation older than ``stale_after_hours``
    stops counting as coverage and the post returns to the rotation.
    """
	published = {p.get("id") for p in posts if p.get("id") is not None}
	total = len(published)
	stale_after = float(config().get("stale_after_hours", 168) or 0)

	fresh = 0
	known_bad = 0
	oldest: Optional[float] = None
	for art_id, row in _ledger(state).items():
		if art_id not in published:
			continue
		age = _age_hours(row["at"], now)
		if age is None:
			continue
		if stale_after > 0 and age > stale_after:
			continue
		fresh += 1
		if not row["ok"]:
			known_bad += 1
		oldest = age if oldest is None else max(oldest, age)

	return {
		"published_total": total,
		"covered": fresh,
		"unverified": max(total - fresh, 0),
		"coverage_complete": total > 0 and fresh >= total,
		# Posts observed to carry no ask, whether or not they were in *this*
		# cycle's sample. This is the number a reader is affected by; the
		# per-cycle `without_footer` only ever describes the current sample.
		"known_without_footer": known_bad,
		"oldest_check_age_hours": None if oldest is None else round(oldest, 1),
	}


def _age_hours(at: str, now: datetime) -> Optional[float]:
	"""Hours since an ISO timestamp, or ``None`` if it cannot be read."""
	parsed = _shared.parse_dt(at)
	if parsed is None:
		return None
	if parsed.tzinfo is None:
		parsed = parsed.replace(tzinfo=timezone.utc)
	return max((now - parsed).total_seconds() / 3600.0, 0.0)


def run(llm: Any = None, status: dict | None = None) -> list[dict]:
	"""Product entry point: ``run(llm, status)``, like every other product.

    ``llm`` is accepted and unused. Asking a model whether a footer is present
    would make the check itself unreliable, and the comparison is exact.
    """
	status = status if isinstance(status, dict) else {}
	action = _run(status, os.getenv("DEV_TO_API_KEY", ""))
	if action.get("_quiet"):
		return []
	action.pop("_quiet", None)
	return [action]


def _run(status: dict, api_key: str = "", published: list | None = None) -> dict:
	"""Observe published posts and record whether readers can actually pay.

    ``published`` is the list ``articles._refresh_stats`` already fetched, used
    only for ids and view counts. Never raises: this is measurement, and losing
    a cycle over a measurement would trade the working system for a note about
    the working system.
    """
	action: dict[str, Any] = {
		"platform": "dev.to-receipt-check",
		"success": False,
		# Observing an ask is not receiving money, exactly as publishing one is
		# not. Real revenue is the on-chain balance, only ever that.
		"estimated_usd": 0.0,
	}
	try:
		cfg = config()
		state = _state(status)

		if not cfg.get("enabled"):
			action["error"] = "disabled in config"
			action["_quiet"] = True
			state["last_reason"] = "disabled"
			return action

		posts = published
		if posts is None:
			from . import devto_stats
			posts = devto_stats.fetch_published(api_key)
		if not posts:
			action["error"] = "no published posts to verify"
			action["_quiet"] = True
			state["last_reason"] = "no_posts"
			return action

		now = datetime.now(timezone.utc)
		history = _seen_map(state)
		found = verify(posts, payout.config(),
					   int(cfg.get("max_per_cycle", 5)), history)

		observed = found.pop("observed", {})
		state.update(found)
		state["last_run"] = now.isoformat()

		# Age the posts observed this cycle, then recompute coverage over the
		# whole catalogue. This is the half `checked` cannot express: `checked`
		# is a sample size, and a sample size read as a coverage figure is how
		# "all_verified" came to describe 5 posts out of 13.
		_record_seen(state, observed, now, posts,
					 int(cfg.get("history_limit", 50)))
		coverage = _coverage(state, posts, now)
		state.update(coverage)

		# The comparison that would have caught the fourteen-cycle outage: the
		# backfill's own claim, set beside an observation made from outside it.
		# Disagreement means a self-reported field is wrong, and the observation
		# is the one to believe.
		#
		# `remaining` is a claim about *every* published post, so it can only be
		# checked against an observation of every published post. Comparing it
		# to a 5-post sample let `agrees_with_backfill: true` stand while eight
		# posts had never been looked at -- agreement computed from evidence
		# that could not have produced disagreement. Until coverage is complete
		# the honest answer is `None`: not yet checkable.
		claimed = status.get("backfill", {}).get("remaining")
		# The gap is judged on everything known, not on this cycle's sample. A
		# post found footerless last cycle is still footerless to a reader
		# today, and rotating past it must not clear the alarm.
		observed_gap = coverage["known_without_footer"] > 0
		if claimed is None or not coverage["coverage_complete"]:
			state["agrees_with_backfill"] = None
		else:
			state["agrees_with_backfill"] = (int(claimed) > 0) == observed_gap

		if found["checked"] == 0:
			state["last_reason"] = "unreachable"
			action["error"] = "could not read any published post"
			action["_quiet"] = True
			return action

		limit = max(1, int(cfg.get("history_limit", 50)))
		del state["missing"][limit:]

		action["covered"] = coverage["covered"]
		action["published_total"] = coverage["published_total"]
		action["unverified"] = coverage["unverified"]
		state["known_without_footer"] = coverage["known_without_footer"]

		if observed_gap:
			state["last_reason"] = "footer_missing"
			gap = coverage["known_without_footer"]
			# Loud, because this is the state that looked fine for fourteen
			# cycles. A reader on that post has no way to pay right now.
			if found["missing"]:
				worst = found["missing"][0]
				log.warning(
					"[receipt_check] %d published post(s) carry NO ask -- "
					"worst this cycle: %s (%d views)",
					gap, worst["title"], worst["views"],
				)
			else:
				# Found in an earlier cycle and not re-sampled this one. Still
				# broken for every reader who lands on it.
				log.warning(
					"[receipt_check] %d published post(s) carry NO ask "
					"(observed in an earlier cycle, not re-sampled this one)",
					gap,
				)
			action["error"] = (
				f"{gap} published post(s) show readers no way to pay"
			)
		elif coverage["coverage_complete"]:
			state["last_reason"] = "all_verified"
			log.info("[receipt_check] all %d published posts carry the ask",
					 coverage["covered"])
		else:
			# Nothing wrong was found, and that is not the same as nothing being
			# wrong. Saying so is the entire point of the module: an unverified
			# post is unverified, never covered, and the reason field must not
			# launder a partial scan into a completion signal.
			state["last_reason"] = "partially_verified"
			log.info(
				"[receipt_check] %d of %d published posts verified, "
				"%d not yet observed",
				coverage["covered"], coverage["published_total"],
				coverage["unverified"],
			)

		# Success means the check ran and produced a trustworthy answer, not
		# that the answer was good news. A verifier reported as failing whenever
		# it finds a problem is one the next cycle is tempted to switch off.
		action["success"] = True
		action["checked"] = found["checked"]
		action["with_footer"] = found["with_footer"]
		action["without_footer"] = found["without_footer"]
		# Nothing to report on the ordinary path where everything is fine.
		if not observed_gap:
			action["_quiet"] = True
		return action
	except Exception as exc:                       # pragma: no cover - defensive
		log.warning("[receipt_check] skipped: %s", exc)
		action["error"] = str(exc)[:200]
		return action
