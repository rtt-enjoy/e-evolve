"""
dev.to performance stats — the feedback loop for article reach.

Reads the owner's own published articles and their view counts, so ``articles``
can tell which subjects earned attention and write a deeper follow-up instead of
guessing blind.

Read-only. Uses the same DEV_TO_API_KEY as publishing. No new secret.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import requests

log = logging.getLogger(__name__)

_API = "https://dev.to/api/articles/me/published"

# dev.to caps per_page at 1000; one page of 100 covers far more history than the
# follow-up window needs.
_PER_PAGE = 100
_TIMEOUT = 20


def fetch_published(api_key: str = "") -> list[dict[str, Any]]:
	"""Return the owner's published articles with view counts, newest first.

    Each item: {id, title, url, tags, page_views, reactions, comments,
    published_at}. Returns [] on any failure -- stats are an optimisation, so a
    dev.to outage must never break a cycle.
    """
	key = (api_key or os.getenv("DEV_TO_API_KEY", "")).strip()
	if not key:
		return []

	try:
		resp = requests.get(
			_API,
			headers={"api-key": key, "Accept": "application/vnd.forem.api-v1+json"},
			params={"per_page": _PER_PAGE, "page": 1},
			timeout=_TIMEOUT,
		)
		resp.raise_for_status()
		raw = resp.json()
	except Exception as exc:
		log.warning("[devto_stats] fetch failed: %s", exc)
		return []

	if not isinstance(raw, list):
		log.warning("[devto_stats] unexpected response shape: %s", type(raw).__name__)
		return []

	out: list[dict[str, Any]] = []
	for item in raw:
		if not isinstance(item, dict):
			continue
		title = str(item.get("title") or "").strip()
		if not title:
			continue
		out.append({
			"id": item.get("id"),
			"title": title,
			"url": str(item.get("url") or ""),
			"tags": [str(t) for t in (item.get("tag_list") or [])],
			# page_views_count is only present when the key owns the article.
			"page_views": int(item.get("page_views_count") or 0),
			"reactions": int(item.get("positive_reactions_count") or 0),
			"comments": int(item.get("comments_count") or 0),
			"published_at": str(item.get("published_at") or ""),
			"description": str(item.get("description") or ""),
		})
	return out


def engagement_score(article: dict[str, Any]) -> float:
	"""Rank an article by attention earned, not just raw views.

    A reaction is a much stronger signal than a view -- it means someone read to
    the end and thought it was worth marking. A comment is stronger still.
    Weighting them keeps a single lucky aggregator link from outranking a post
    that genuinely landed.
    """
	return (
		float(article.get("page_views", 0))
		+ 25.0 * float(article.get("reactions", 0))
		+ 50.0 * float(article.get("comments", 0))
	)


def top_performer(
	articles: list[dict[str, Any]],
	within_hours: int = 48,
	min_views: int = 1,
	exclude_ids: Optional[set] = None,
) -> Optional[dict[str, Any]]:
	"""Return the best-performing recent article, or None.

    ``within_hours`` bounds the window to genuinely recent posts -- the point is
    to follow up while the subject is still live, not to resurrect a post from
    last month. Articles already followed up (``exclude_ids``) are skipped so the
    same winner is not mined twice.
    """
	if not articles:
		return None

	excluded = exclude_ids or set()
	cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, within_hours))
	ranked: list[tuple[float, dict[str, Any]]] = []

	for art in articles:
		if art.get("id") in excluded:
			continue
		if int(art.get("page_views", 0)) < min_views:
			continue
		published = _parse_dt(art.get("published_at", ""))
		# A missing timestamp is not a reason to consider an unbounded-age post.
		if not published or published < cutoff:
			continue
		ranked.append((engagement_score(art), art))

	if not ranked:
		return None
	ranked.sort(key=lambda pair: pair[0], reverse=True)
	best = ranked[0][1]
	log.info(
		"[devto_stats] top performer: %r (%d views, %d reactions)",
		best.get("title", "")[:60], best.get("page_views", 0), best.get("reactions", 0),
	)
	return best


def summarize(articles: list[dict[str, Any]]) -> dict[str, Any]:
	"""Aggregate stats for the dashboard and for status.json."""
	if not articles:
		return {"count": 0, "total_views": 0, "avg_views": 0.0, "best_title": "", "best_views": 0}
	views = [int(a.get("page_views", 0)) for a in articles]
	best = max(articles, key=engagement_score)
	return {
		"count": len(articles),
		"total_views": sum(views),
		"avg_views": round(sum(views) / len(views), 1),
		"best_title": best.get("title", ""),
		"best_views": int(best.get("page_views", 0)),
		"best_url": best.get("url", ""),
	}


def winning_tags(articles: list[dict[str, Any]], top_n: int = 6) -> list[str]:
	"""Tags that correlate with views on this account, best first.

    Averaged per tag rather than summed, so a tag used once on a hit is not
    buried by a tag used twenty times on quiet posts.
    """
	buckets: dict[str, list[float]] = {}
	for art in articles:
		score = engagement_score(art)
		for tag in art.get("tags", []):
			slug = str(tag).strip().lower()
			if slug:
				buckets.setdefault(slug, []).append(score)
	averaged = [(sum(v) / len(v), tag) for tag, v in buckets.items()]
	averaged.sort(reverse=True)
	return [tag for _, tag in averaged[:top_n]]


def _parse_dt(value: str) -> Optional[datetime]:
	"""Parse dev.to's ISO timestamps, tolerating 'Z' and naive values."""
	text = str(value or "").strip()
	if not text:
		return None
	try:
		parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
	except ValueError:
		return None
	if parsed.tzinfo is None:
		parsed = parsed.replace(tzinfo=timezone.utc)
	return parsed
