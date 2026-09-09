"""
Earning Module — Receipt Check (dev.to footer verification)

Verifies that every published article has the support footer with the USDT
receive address. This is the feedback loop for the payout module.

Activates with: DEV_TO_API_KEY. Without it the module skips silently.

Returns a list of actions with platform='receipt_check' for the dashboard.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from . import devto, payout
from ._shared import hours_until_due, load_config

log = logging.getLogger(__name__)

_PLATFORM = "receipt_check"

_DEFAULTS = {
	"enabled": True,
	"check_interval_hours": 24,
	"history_limit": 200,
}


def _config() -> dict:
	"""Strategy config for this module, defaults filled in for missing keys."""
	return load_config("receipt_check", _DEFAULTS)



def run(llm: Any = None, status: dict | None = None) -> list[dict]:
	"""Main entry point: verify footer on all published articles."""
	status = status if isinstance(status, dict) else {}
	cfg = _config()
	
	if not cfg.get("enabled", True):
		log.debug("[receipt_check] disabled in config — skipping")
		return []

	api_key = os.getenv("DEV_TO_API_KEY", "").strip()
	if not api_key:
		log.debug("[receipt_check] DEV_TO_API_KEY not set — skipping")
		return []

	forced = bool(status.get("_overrides", {}).get("force_receipt_check"))
	if not forced:
		waiting = hours_until_due(status.get("receipt_check", {}), "last_run", int(cfg.get("check_interval_hours", 24)))
		if waiting > 0:
			log.info("[receipt_check] next check due in %.1fh — skipping", waiting)
			return []
	else:
		log.info("[receipt_check] interval bypassed by 'force receipt_check' command")

	# Get published articles
	articles = devto.fetch_published(api_key)
	if not articles:
		log.warning("[receipt_check] no published articles found")
		return [{
			"platform": _PLATFORM,
			"success": False,
			"error": "no published articles found",
			"estimated_usd": 0.0,
		}]

	# Check each article for footer
	checked = 0
	with_footer = 0
	without_footer = 0
	unreachable = 0
	missing = []

	for article in articles:
		article_id = article.get("id")
		article_url = article.get("url", "")
		title = article.get("title", "")[:60]
		
		checked += 1
		
		# Check if body has footer
		body = article.get("body_markdown", "")
		footer = payout.footer()
		
		if footer and footer.get("heading") in body:
			with_footer += 1
			log.debug("[receipt_check] %s has footer", title)
		else:
			without_footer += 1
			missing.append({
				"id": article_id,
				"title": title,
				"url": article_url,
			})
			log.info("[receipt_check] %s missing footer", title)

	# Update state
	from datetime import datetime, timezone
	now = datetime.now(timezone.utc)
	state = status.setdefault("receipt_check", {})
	state["last_run"] = now.isoformat()
	state["checked"] = checked
	state["with_footer"] = with_footer
	state["without_footer"] = without_footer
	state["unreachable"] = unreachable
	state["missing"] = missing
	state["total"] = checked
	state["covered"] = with_footer
	state["unverified"] = without_footer
	state["coverage_complete"] = (without_footer == 0)
	state["oldest_check_age_hours"] = 0
	
	# Record verified IDs
	verified_ids = []
	for article in articles:
		article_id = article.get("id")
		body = article.get("body_markdown", "")
		footer = payout.footer()
		if footer and footer.get("heading") in body:
			verified_ids.append({
				"id": article_id,
				"at": now.isoformat(),
				"ok": True,
			})
	
	state["verified_ids"] = verified_ids

	log.info(
		"[receipt_check] checked %d articles: %d with footer, %d without", 
		checked, with_footer, without_footer
	)

	return [{
		"platform": _PLATFORM,
		"success": True,
		"checked": checked,
		"with_footer": with_footer,
		"without_footer": without_footer,
		"unreachable": unreachable,
		"missing": missing,
		"estimated_usd": 0.0,
	}]


__all__ = ["run"]