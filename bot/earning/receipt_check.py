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


def verify(posts: list[dict[str, Any]], cfg: dict[str, Any] | None = None,
		   limit: int = 5) -> dict[str, Any]:
	"""Check the highest-traffic ``limit`` posts for a reader-visible ask.

    Takes the post list only for ids and view counts -- the body is always
    re-fetched from the public endpoint, never read from the caller's data.
    That separation is the whole value of this function.
    """
	payout_cfg = cfg or payout.config()
	ranked = sorted(
		(p for p in posts if p.get("id") is not None),
		key=lambda p: int(p.get("page_views") or 0),
		reverse=True,
	)[:max(1, int(limit))]

	result: dict[str, Any] = {
		"checked": 0, "with_footer": 0, "without_footer": 0,
		"unreachable": 0, "missing": [],
	}

	for post in ranked:
		body = fetch_live_body(int(post["id"]))
		if body is None:
			result["unreachable"] += 1
			continue
		result["checked"] += 1
		if payout.has_footer(body, payout_cfg):
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

		found = verify(posts, payout.config(), int(cfg.get("max_per_cycle", 5)))

		state.update(found)
		state["last_run"] = datetime.now(timezone.utc).isoformat()

		# The comparison that would have caught the fourteen-cycle outage: the
		# backfill's own claim, set beside an observation made from outside it.
		# Disagreement means a self-reported field is wrong, and the observation
		# is the one to believe.
		claimed = status.get("backfill", {}).get("remaining")
		observed_gap = found["without_footer"] > 0
		if claimed is None:
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

		if observed_gap:
			state["last_reason"] = "footer_missing"
			worst = found["missing"][0]
			# Loud, because this is the state that looked fine for fourteen
			# cycles. A reader on that post has no way to pay right now.
			log.warning(
				"[receipt_check] %d of %d checked posts carry NO ask -- "
				"worst: %s (%d views)",
				found["without_footer"], found["checked"],
				worst["title"], worst["views"],
			)
			action["error"] = (
				f"{found['without_footer']} published post(s) show readers "
				f"no way to pay"
			)
		else:
			state["last_reason"] = "all_verified"
			log.info("[receipt_check] all %d checked posts carry the ask",
					 found["checked"])

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
