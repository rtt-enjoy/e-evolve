"""
Earning Module \u2014 Newsletter Digest (dev.to)

Publishes a recurring "what shipped in tech" digest built from real trending
stories found by ``trending``. Where ``articles`` writes one deep piece about a
single source, this writes one short paragraph about each of several sources.

Activates with: DEV_TO_API_KEY. Without it the module skips silently.

Quality gates and the dev.to call come from ``devto`` rather than being
reimplemented -- the two modules publish to the same platform under the same
house style, so they must not drift apart. Structural checks stay local
(``_digest_problems``), because a digest legitimately lacks the essay rules
``articles`` asserts.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Optional

from . import devto, trending
from ._shared import bounded_append, hours_until_due, load_config

log = logging.getLogger(__name__)

# dev.to breakdown key. Distinct from the "dev.to" articles use, so the two
# products stay separately visible in earnings["breakdown"].
_PLATFORM = "dev.to-newsletter"

_DEFAULTS = {
	"enabled": True,
	"min_interval_hours": 168,
	"items_per_issue": 7,
	"min_items": 4,
	"source_max_age_hours": 168,
	"history_limit": 200,
	"min_words": 500,
	# Empty means today's behaviour: a general developer digest. Set it to angle
	# every issue for one audience -- the source article's point that a narrow
	# niche beats a broad one. Choosing the niche is the owner's call.
	"niche_focus": "",
}


def _config() -> dict:
	"""Strategy config for this module, defaults filled in for missing keys."""
	return load_config("newsletter", _DEFAULTS)


_SYSTEM = """\
You are a senior engineer writing a short weekly digest for other developers on dev.to.

You are given several REAL trending technology stories from the past week. Write a
digest that covers each one briefly and usefully.

Respond with ONLY a single JSON object.

Schema:
{
  "title": "specific digest title naming the week's theme (max 80 chars)",
  "description": "one-sentence summary (max 150 chars)",
  "body_markdown": "full digest in markdown",
  "tags": ["news", "programming", "ai"]
}

STRUCTURE -- a digest, not an essay:
- Open with 2-3 sentences on what connects this week's stories. No "In today's world".
- One `##` section per story, in the order given. Never use `#` (the title owns it).
- Each `##` heading states the story's outcome in your own words. Do NOT copy the
  source headline verbatim, and do NOT number your headings.
- Leave one blank line after every heading, before the paragraph that follows it.
- Under each heading write 2-4 short paragraphs covering, in this order:
    1. What actually happened or shipped.
    2. Why it matters to a working developer.
    3. Who should care, and what they might do about it.
- End every story section with a source line exactly like this, on its own line:
  `Source: [<source title>](<source url>)`
  Use the exact URL given to you. Never invent, shorten, or alter a URL.
- Close with a `## What I'd Watch Next` section of 2-4 bullets.

VOICE -- plain-spoken, like a colleague summarizing the week:
- Warm and direct. Address the reader as "you". Use "I" for your own read on things.
  Contractions are good ("it's", "you'll", "doesn't").
- Short, clean sentences. One idea each.
- Prefer the simple word: "use" over "utilize", "start" over "commence", "about"
  over "approximately", "so" over "consequently".
- Explain jargon the first time you use it, in one short clause.
- No "simply", "just", or "obviously". No hype, no exclamation marks.
- Calm and factual. You are reporting, not selling.

CONTENT RULES:
- Be accurate and specific. Real library names, real project names.
- Never invent benchmarks, pricing, citations, version numbers, or dates.
- This is the rule most often broken: do NOT state latency figures, model
  parameter counts, token prices, throughput, or rate limits as fact. If a
  number matters, describe it qualitatively or tell the reader to check the docs.
- Do not build spec tables. A table of latency, sizes, or prices will be deleted.
- Work only from the summary you are given. If a summary is thin, say less about
  that story rather than guessing at details.
- Never claim you tested, benchmarked, or ran any of this yourself.
- No promotional fluff, no income claims, no "revolutionary"/"game-changing"."""


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
	"""Main entry point for the newsletter earning module."""
	cfg = _config()
	state = status.setdefault("newsletter_daily", {})

	if not cfg.get("enabled", True):
		state["enabled"] = False
		log.debug("[newsletter] disabled in strategy config \u2014 skipping")
		return []
	state["enabled"] = True

	api_key = os.getenv("DEV_TO_API_KEY", "").strip()
	if not api_key:
		log.debug("[newsletter] DEV_TO_API_KEY not set \u2014 skipping")
		return []

	forced = bool(status.get("_overrides", {}).get("force_newsletter"))
	if not forced:
		waiting = hours_until_due(state, "published_at", int(cfg["min_interval_hours"]))
		if waiting > 0:
			log.info("[newsletter] next issue due in %.1fh \u2014 skipping", waiting)
			return []
	else:
		log.info("[newsletter] cadence bypassed by 'force newsletter' command")

	if not llm:
		log.warning("[newsletter] no LLM available \u2014 publishing nothing")
		return []

	issue = _generate_issue(llm, status, cfg)
	if not issue:
		return [{
			"platform": _PLATFORM,
			"success": False,
			"skipped": True,
			"error": "not enough fresh trending sources or LLM output unusable",
			"estimated_usd": 0.0,
		}]

	items = issue.pop("_items", [])
	result = devto.publish(issue, api_key)
	result["platform"] = _PLATFORM
	result["item_count"] = len(items)

	if result.get("success"):
		now = datetime.now(timezone.utc)
		state["date"] = now.date().isoformat()
		state["published_at"] = now.isoformat()
		state["published"] = int(state.get("published", 0)) + 1
		state["last_item_count"] = len(items)
		state["last_title"] = issue.get("title", "")
		state["last_url"] = result.get("url", "")
		# Record before returning so a story can never be featured twice, even if
		# a later phase of the cycle fails.
		_record_issue(status, items, int(cfg["history_limit"]))

	return [result]


def _generate_issue(llm: Any, status: dict, cfg: dict) -> Optional[dict]:
	"""Build one digest from fresh trending stories.

    Returns None when too few unused sources are available or the LLM output
    fails a gate. Publishing nothing is correct -- a thin or recycled digest is
    worse than no digest.
    """
	items = _pick_sources(status, cfg)
	min_items = int(cfg["min_items"])
	if len(items) < min_items:
		log.warning(
			"[newsletter] only %d fresh source(s), need %d \u2014 publishing nothing",
			len(items), min_items,
		)
		return None

	log.info("[newsletter] building digest from %d sources", len(items))

	prompt = (
		"Write this week's developer digest from the stories below. Cover them in "
		"the order given, one `##` section each, following every structure and "
		"voice rule in the system prompt. Use each URL exactly as written. "
		"JSON only.\n\n"
		+ "\n\n".join(_format_item(i, item) for i, item in enumerate(items, 1))
	)

	# Angle the issue for one audience when the owner has chosen one. Appended to
	# the prompt, not to _SYSTEM: that constant is shared with the tone gates and
	# must stay stable.
	niche = str(cfg.get("niche_focus", "")).strip()
	if niche:
		prompt += (
			f"\n\nAudience focus: write for {niche}. When a story matters more to "
			f"that audience, say why in that section. Do not drop a story to fit "
			f"the niche -- cover all of them, angled for this reader."
		)

	try:
		if hasattr(llm, "complete_json_for_role"):
			data = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=6000)
		else:
			data = llm.complete_json(prompt, system=_SYSTEM, max_tokens=6000)
	except Exception as exc:
		log.warning("[newsletter] LLM generation failed: %s \u2014 publishing nothing", exc)
		return None

	if not (data.get("title") and data.get("body_markdown")):
		log.warning("[newsletter] LLM returned no usable digest \u2014 publishing nothing")
		return None

	# Deterministic cleanup first, so no LLM call is spent on fixable artifacts.
	issue = devto.normalize(data)
	issue["body_markdown"], dropped = devto.strip_fabricated_tables(issue["body_markdown"])
	if dropped:
		log.info("[newsletter] removed %d fabricated spec table(s)", dropped)

	issue["body_markdown"] = _ensure_sources(issue["body_markdown"], items)

	problems = _digest_problems(issue["body_markdown"], items, cfg)
	if problems:
		log.warning("[newsletter] %s \u2014 publishing nothing", "; ".join(problems))
		return None

	issue["_items"] = items
	return issue


def _format_item(index: int, item: dict) -> str:
	"""Render one source into the prompt block the model reads."""
	summary = str(item.get("summary", "")).strip()[:1200]
	return (
		f"STORY {index}\n"
		f"TITLE: {item.get('title', '')}\n"
		f"URL: {item.get('url', '')}\n"
		f"PUBLISHER: {item.get('source', '')}\n"
		f"SUMMARY: {summary or '(no summary available; keep this section brief)'}"
	)


def _pick_sources(status: dict, cfg: dict) -> list[dict]:
	"""Return the top unused trending candidates for this issue.

    Excludes both the newsletter's own history (so a story never appears in two
    digests) and the articles module's history (so a story that became a daily
    deep-dive is not also paraphrased in a digest the same week). Two modules,
    two products: the same story being both a digest paragraph AND a separate
    full article is fine, but the same story being both a digest AND a digest
    is the repeat the newsletter_history list exists to prevent.
    """
	try:
		candidates = trending.fetch_candidates(
			max_age_hours=int(cfg["source_max_age_hours"]), limit=40
		)
	except Exception as exc:
		log.warning("[newsletter] trending fetch failed: %s", exc)
		return []

	hist = _history(status)
	article_hist = status.get("article_history") or {}
	used_urls = set(hist.get("source_urls", [])) | set(article_hist.get("source_urls", []))
	used_titles = set(hist.get("source_titles", [])) | set(article_hist.get("source_titles", []))

	picked: list[dict] = []
	for item in candidates:
		url_key = trending._canonical_url(item.get("url", ""))
		title_key = trending.normalize_title(item.get("title", ""))
		if not url_key or not item.get("title"):
			continue
		if url_key in used_urls or (title_key and title_key in used_titles):
			continue
		# Guard against one fetch returning the same story twice.
		used_urls.add(url_key)
		if title_key:
			used_titles.add(title_key)
		picked.append(item)
		if len(picked) >= int(cfg["items_per_issue"]):
			break
	return picked


def _history(status: dict) -> dict:
	"""Persistent record of stories already featured in a digest.

    Kept separate from ``article_history`` on purpose: a story can legitimately
    be both a digest paragraph and, later, a full article. Sharing one history
    would starve both modules.
    """
	return status.setdefault("newsletter_history", {})


def _record_issue(status: dict, items: list[dict], limit: int) -> None:
	"""Remember every featured story so it is never featured again."""
	hist = _history(status)
	for item in items:
		for key, value in (
			("source_urls", trending._canonical_url(item.get("url", ""))),
			("source_titles", trending.normalize_title(item.get("title", ""))),
		):
			if not value:
				continue
			bounded_append(hist.setdefault(key, []), value, limit)


def _ensure_sources(body: str, items: list[dict]) -> str:
	"""Append any source link the model dropped.

    Attribution is mandatory, and a missing link is the one digest fault worth
    repairing deterministically rather than rejecting the whole issue over.
    """
	missing = [i for i in items if str(i.get("url", "")).strip() and str(i["url"]) not in body]
	if not missing:
		return body
	log.info("[newsletter] appending %d missing source link(s)", len(missing))
	lines = [
		f"- [{str(i.get('title', '')).strip() or i['url']}]({i['url']})"
		for i in missing
	]
	return body.rstrip() + "\n\n## Also Covered\n\n" + "\n".join(lines) + "\n"


def _digest_problems(body: str, items: list[dict], cfg: dict) -> list[str]:
	"""Return digest-shaped rule violations.

    ``articles._format_problems`` asserts essay rules -- code blocks and a Key
    Takeaways section -- that a digest legitimately lacks, so the structural
    checks are local. The fabrication and tone checks are shared, because those
    rules apply to anything published under this byline.
    """
	problems: list[str] = []

	words = len(body.split())
	min_words = int(cfg["min_words"])
	if words < min_words:
		problems.append(f"too short ({words} words, need {min_words}+)")

	sections = len(re.findall(r"^## ", body, re.MULTILINE))
	min_items = int(cfg["min_items"])
	if sections < min_items:
		problems.append(f"only {sections} '##' sections, need {min_items}+")

	if re.search(r"^# ", body, re.MULTILINE):
		problems.append("uses a top-level '#' heading")

	missing = [
		str(i.get("url", "")) for i in items
		if str(i.get("url", "")).strip() and str(i["url"]) not in body
	]
	if missing:
		problems.append(f"{len(missing)} source link(s) missing from body")

	problems.extend(devto.fabrication_problems(body))
	problems.extend(devto.tone_problems(body))
	return problems