"""
Put the receive path onto the articles that already have the readers.

``payout`` covers new posts, while this module appends the same deterministic
footer to older posts. It never edits prose or invokes an LLM: live articles
already earned their reach, and rewriting them would create an unnecessary
quality risk.

The state file records both completed IDs and unresolved update failures. A
post that has since been updated, or that no longer needs a footer, must not
keep an old 429 note forever. This module therefore clears only resolved skip
records; failures for posts that still need work remain visible for the next
cycle.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from . import _shared, devto, devto_stats, payout

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
	"enabled": True,
	# Per cycle, not total. The cap keeps one bad cycle from touching the whole
	# catalogue and stays comfortably below Forem's article-update limit.
	"max_per_cycle": 3,
	"history_limit": 200,
}


def config() -> dict[str, Any]:
	"""This module's strategy configuration, read at call time."""
	return _shared.load_config("backfill", DEFAULTS)


def _state(status: dict) -> dict:
	return status.setdefault("backfill", {
		"done_ids": [],
		"skipped": {},
		"updated_total": 0,
		"last_run": None,
		"last_reason": None,
	})


def _clear_resolved_skips(state: dict[str, Any], candidate_ids: set[str]) -> None:
	"""Remove failure notes for posts that are complete or no longer editable."""
	skipped = state.get("skipped")
	if not isinstance(skipped, dict):
		skipped = {}
		state["skipped"] = skipped

	done = {
		str(article_id)
		for article_id in (state.get("done_ids") or [])
		if article_id is not None
	}
	for article_id in list(skipped):
		key = str(article_id)
		if key in done or key not in candidate_ids:
			skipped.pop(article_id, None)


def needs_footer(post: dict, cfg: dict[str, Any] | None = None) -> bool:
	"""Return whether a live post has a usable body without the payout footer."""
	body = str(post.get("body_markdown") or "")
	if not body.strip():
		return False
	if devto.has_front_matter(body):
		return False
	return not payout.has_footer(body, cfg)


def run(llm: Any = None, status: dict | None = None) -> list[dict]:
	"""Append the payout footer to a bounded batch of older articles.

	``llm`` is intentionally unused: this operation is deterministic and must
	never spend an LLM request rewriting live prose.
	"""
	status = status if isinstance(status, dict) else {}
	action = _run(status, os.getenv("DEV_TO_API_KEY", ""))
	if action.get("_quiet"):
		return []
	action.pop("_quiet", None)
	return [action]


def _run(status: dict, api_key: str = "", published: list | None = None) -> dict:
	"""Update eligible posts and return a bounded action result."""
	action: dict[str, Any] = {
		"platform": "dev.to-backfill",
		"success": False,
		"updated": 0,
		# Adding an ask is not revenue; only an on-chain receipt can be counted.
		"estimated_usd": 0.0,
	}
	try:
		cfg = config()
		state = _state(status)
		if not isinstance(state.get("skipped"), dict):
			state["skipped"] = {}

		if not cfg.get("enabled"):
			action["error"] = "disabled in config"
			action["_quiet"] = True
			state["last_reason"] = "disabled"
			return action

		if not payout.footer():
			action["error"] = "payout footer not live"
			action["_quiet"] = True
			state["last_reason"] = "payout_not_live"
			return action

		key = (api_key or "").strip()
		if not key:
			action["error"] = "no dev.to api key"
			action["_quiet"] = True
			state["last_reason"] = "no_key"
			return action

		posts = published if published is not None else devto_stats.fetch_published(key)
		if not posts:
			action["error"] = "no published posts available"
			action["_quiet"] = True
			state["last_reason"] = "no_posts"
			return action

		payout_cfg = payout.config()
		done = {
			str(article_id)
			for article_id in (state.get("done_ids") or [])
			if article_id is not None
		}
		# Build the unresolved set once. It is used both for selection and for
		# deciding which historical skip notes are still meaningful.
		candidate_ids = {
			str(post["id"])
			for post in posts
			if post.get("id") is not None
			and str(post["id"]) not in done
			and needs_footer(post, payout_cfg)
		}
		_clear_resolved_skips(state, candidate_ids)
		candidates = [
			post for post in posts
			if str(post.get("id")) in candidate_ids
		]

		if not candidates:
			action["success"] = True
			action["_quiet"] = True
			state["last_reason"] = "nothing_to_do"
			state["last_run"] = datetime.now(timezone.utc).isoformat()
			state["remaining"] = 0
			state["skipped"] = {}
			log.info("[backfill] every published post already carries the footer")
			return action

		# The oldest and most-viewed posts get the first bounded write batch.
		candidates.sort(key=lambda post: int(post.get("page_views") or 0), reverse=True)

		updated = 0
		batch_size = max(1, int(cfg.get("max_per_cycle", 3)))
		for post in candidates[:batch_size]:
			body = str(post.get("body_markdown") or "")
			footered = payout.add_footer({"body_markdown": body}, payout_cfg)
			new_body = str(footered.get("body_markdown") or "")
			if new_body == body or not payout.has_footer(new_body, payout_cfg):
				continue

			result = devto.update_body(int(post["id"]), new_body, key)
			if result.get("success"):
				updated += 1
				state.setdefault("done_ids", []).append(post["id"])
				# A previous 429 is no longer an unresolved failure once this
				# PUT succeeds. Keeping it would make a completed backfill look
				# permanently broken in status.json.
				state.setdefault("skipped", {}).pop(str(post["id"]), None)
				log.info(
					"[backfill] footer added to %s (%s views)",
					str(post.get("title", ""))[:60], post.get("page_views"),
				)
			else:
				state.setdefault("skipped", {})[str(post["id"])] = result.get("error", "")
				# A rate-limit or server failure is a reason to stop rather than
				# hammer the API with the rest of the batch.
				break

		limit = max(1, int(cfg.get("history_limit", 200)))
		seen: set = set()
		deduped = []
		for article_id in state.get("done_ids", []):
			if article_id is None:
				continue
			key = str(article_id)
			if key not in seen:
				seen.add(key)
				deduped.append(article_id)
		state["done_ids"] = deduped[-limit:]
		state["skipped"] = dict(list(state["skipped"].items())[-limit:])
		state["updated_total"] = int(state.get("updated_total", 0)) + updated
		state["last_run"] = datetime.now(timezone.utc).isoformat()
		state["remaining"] = max(len(candidates) - updated, 0)
		state["last_reason"] = "updated" if updated else "update_failed"

		action["success"] = updated > 0
		action["updated"] = updated
		action["remaining"] = state["remaining"]
		if not updated:
			action["error"] = "no post could be updated"
		return action
	except Exception as exc:  # pragma: no cover - defensive boundary
		log.warning("[backfill] skipped: %s", exc)
		action["error"] = str(exc)[:200]
		return action