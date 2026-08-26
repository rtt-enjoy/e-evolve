"""
Earning Module — Articles (dev.to)
Generates and publishes one original technical article per day to dev.to,
written from a real trending source found by ``trending``.

Activates with: DEV_TO_API_KEY. Without it the module skips silently.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Optional

import requests

from . import devto_stats, trending

log = logging.getLogger(__name__)

_CONFIG_FILE = Path("config/strategy.json")

def _load_config() -> dict:
	try:
		import json
		return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
	except Exception:
		return {}

_article_config = _load_config().get("articles", {})
_MAX_ARTICLES_PER_CYCLE = int(_article_config.get("max_articles_per_cycle", 1))
_MIN_INTERVAL_HOURS = int(_article_config.get("min_interval_hours", 6))
_SOURCE_MAX_AGE_HOURS = int(_article_config.get("source_max_age_hours", 24))
# How many past titles/sources to remember for duplicate detection.
_HISTORY_LIMIT = int(_article_config.get("history_limit", 200))
_MIN_WORDS = int(_article_config.get("min_words", 700))
# Follow-up behaviour: mine the best recent post for a deeper second article.
_FOLLOWUP_ENABLED = bool(_article_config.get("followup_enabled", True))
_FOLLOWUP_WINDOW_HOURS = int(_article_config.get("followup_window_hours", 48))
_FOLLOWUP_MIN_VIEWS = int(_article_config.get("followup_min_views", 40))
_TITLE_MAX_CHARS = int(_article_config.get("title_max_chars", 70))
_TITLE_MIN_CHARS = int(_article_config.get("title_min_chars", 25))

_SYSTEM = """\
You are a senior engineer writing for a developer audience on dev.to.

You are given a REAL trending technology article as source material. Write your
own substantially better article on the same subject.

Respond with ONLY a single JSON object.

Schema:
{
  "title": "concrete, curiosity-driving title (25-70 chars)",
  "description": "one-sentence summary (max 150 chars)",
  "body_markdown": "full article in markdown",
  "tags": ["python", "ai", "automation"]
}

TITLE -- this decides whether anyone reads the article at all. Spend real effort here:
- 25-70 characters. Long titles get truncated in the dev.to feed and on social cards.
- Lead with the concrete thing at stake. A reader scanning a feed must learn what
  they gain or avoid within the first four words.
- Use ONE of these proven shapes, whichever fits the content honestly:
  * The specific failure: "The Postgres Index That Made Queries Slower"
  * The corrected belief: "I Was Wrong About Async Context Managers"
  * The concrete number: "Three Retry Bugs That Survive Code Review"
  * The direct question a reader is already asking: "Why Is Your Docker Build Slow?"
  * The mechanism revealed: "How Rate Limiters Actually Drop Your Requests"
- Name a real technology, error, or mechanism. "Better Python Code" is invisible;
  "Your Python Retry Loop Is Lying To You" is not.
- Create a curiosity gap and then PAY IT OFF in the body. Never promise something
  the article does not deliver -- dev.to readers punish that in the comments.
- Title Case The Important Words. It reads as considered, not shouted.
- BANNED in titles: exclamation marks, "Ultimate", "Complete Guide",
  "You NEED to Know", "Amazing", "Mind-blowing", "Secrets", "Hacks",
  "Top 10 ...", "A Deep Dive Into", "Everything You Need To Know",
  and any ALL-CAPS word. These read as spam and suppress clicks here.
- No colon-subtitle padding. "Retries: A Practical Guide to Backoff in Python"
  wastes the scannable half of the line. Pick the sharper half and stop.

TAGS -- tags are how dev.to distributes the post, so treat them as reach, not labels:
- Exactly 4 tags. Fewer costs you feed placement.
- Include at least two large, high-traffic tags a reader actually follows
  (for example: programming, python, javascript, webdev, ai, devops, tutorial,
  beginners, opensource, react, node, typescript, career, productivity).
- Then one or two specific tags matching the real subject.
- Lowercase, letters and digits only, no spaces, no punctuation.

VOICE -- write like a helpful senior colleague explaining something at a whiteboard:
- Warm and plain-spoken. Address the reader as "you". Use "I" for your own
  experience. Contractions are good ("it's", "you'll", "doesn't").
- Short, clean sentences. One idea each. If a sentence needs a comma splice or a
  semicolon to hold together, split it in two.
- Prefer the simple word: "use" over "utilize", "start" over "commence", "about"
  over "approximately", "so" over "consequently".
- Explain jargon the first time you use it, in one short clause. Never assume the
  reader already knows the acronym.
- Encouraging, never condescending. No "simply", "just", or "obviously" -- if it
  were obvious the reader would not be here.
- Calm and factual. No hype, no exclamation marks, no rhetorical questions
  stacked up as a hook.

STRUCTURE -- simple but very organized. The reader must be able to skim headings
and know exactly what the article covers:
- Open with a 2-3 sentence hook stating the concrete problem. No "In today's world".
- Then one short "what you'll learn" line or 3-bullet list, so the reader knows
  the payoff before investing time.
- Use `##` for main sections and `###` for sub-points. Never use `#` (the title owns it).
- 4-7 `##` sections with descriptive, specific headings. Not "Introduction"/"Conclusion".
  A good heading states an outcome ("Cache the Expensive Call"), not a topic ("Caching").
- Do NOT number your headings. Write `## Choose a Strategy`, never `## 2. Choose a Strategy`.
- Leave one blank line after every heading, before the paragraph that follows it.
- Order sections so each one builds on the last. Problem, then approach, then
  implementation, then what breaks.
- Keep paragraphs to 2-4 sentences. Insert a blank line between every block.
- Never stack two headings with no prose between them.

CODE AND TABLES:
- Include at least two fenced code blocks with an explicit language tag
  (```python, ```yaml, ```bash) and code that would actually run.
- Keep each block under ~25 lines. Show the interesting part, not the boilerplate.
- Introduce every code block with one sentence saying what it does, and follow it
  with a short explanation of *why* it is written that way.
- Use a markdown table when comparing 3+ options, but ONLY for qualitative
  comparisons (approach, tradeoff, when-to-use). Never build a table of specs
  you would have to invent: no latency figures, parameter counts, model sizes,
  prices, or benchmark numbers.
- Use bulleted lists for enumerations, but never more than 7 items.
- Bold key terms sparingly with **term**, at most a few per article.
- End with a `## Key Takeaways` section of 3-5 concrete bullets.

CONTENT RULES:
- Be technically accurate and specific. Real library names, real flags.
- Never invent benchmarks, pricing, citations, or version numbers you are unsure of.
- This is the rule most often broken: do NOT state latency figures, model
  parameter counts, token prices, throughput, or rate limits as fact. If a
  number matters, describe it qualitatively ("noticeably slower", "cheaper per
  token") or tell the reader to check the provider's current docs.
- A table with a "Latency" or "Model Size" column will be deleted before
  publishing. Compare on approach and tradeoffs instead.
- No promotional fluff, no income guarantees, no "revolutionary"/"game-changing".
- Write as a practitioner reporting what worked, not a marketer.

SOURCE HANDLING -- this part is mandatory:
- Treat the source as a story lead and a set of facts, NOT as text to reword.
- Never copy sentences or paragraph structure from the source. No paraphrase-by-
  synonym. If a sentence of yours could be diffed against the source and look
  like an edit of it, rewrite it from scratch.
- Your article must ADD what the source lacks: working code the source omits,
  a comparison table, failure modes, tradeoffs, a step-by-step implementation,
  or the practitioner's "what this actually means for your codebase" angle.
- Your title must NOT restate the source title. Choose your own specific angle.
- Quote the source only to disagree or build on it, at most one short sentence,
  clearly marked as a quote.
- Do not claim you performed measurements or ran the source's experiments.
- End the body with an `## Source` section: one line linking the original as
  `[<source title>](<source url>)` and one sentence on what you added."""


# A follow-up post has a different job from a fresh take: the subject is already
# proven to draw readers on this account, so the second piece must go deeper
# rather than re-explain. Sharing _SYSTEM's voice/format rules keeps the two
# paths from drifting apart on style.
_FOLLOWUP_EXTRA = """\

FOLLOW-UP MODE -- you are writing a sequel to an article of mine that readers
actually turned up for. The subject is proven; do not re-explain it.
- Assume the reader may not have read the first post. Recap it in at most two
  sentences, then move past it.
- The value of this piece is DEPTH the first one lacked: the edge case that bites
  in production, the part that is harder than it looked, what you would do
  differently, or the next step a reader hits immediately after the first post.
- Do not restate the first article's structure or reuse its headings.
- Your title must clearly differ from the first article's title while signalling
  the same subject, so a returning reader recognises it and a new reader still
  understands it standalone.
- Link the earlier post once, inline, where a reader would naturally want the
  background -- not as a footnote.
- The `## Source` section still credits the ORIGINAL external source."""

_FOLLOWUP_SYSTEM = _SYSTEM + _FOLLOWUP_EXTRA


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
	"""Main entry point for the articles earning module."""
	devto_api_key = os.getenv("DEV_TO_API_KEY", "").strip()

	if not devto_api_key:
		log.debug("[articles] DEV_TO_API_KEY not set — skipping")
		return []

	# Check rate limiting
	state = status.setdefault("article_daily", {})
	last_date = state.get("date", "")
	from datetime import datetime, timezone
	today = datetime.now(timezone.utc).date().isoformat()
	
	forced = int(status.get("_overrides", {}).get("force_articles", 0) or 0)
	if last_date == today and not forced:
		published_today = state.get("published", 0)
		if published_today >= _MAX_ARTICLES_PER_CYCLE:
			log.info("[articles] Already published %d article(s) today — skipping", published_today)
			return []
	if forced:
		log.info("[articles] daily cap bypassed by 'force articles' command")

	# Generate and publish
	article = _generate_article(llm, status)
	if not article:
		log.warning("[articles] No article generated — publishing nothing this cycle")
		return [{
			"platform": "dev.to",
			"success": False,
			"skipped": True,
			"error": "no fresh trending source or LLM output available",
			"estimated_usd": 0.0,
		}]

	results = []

	# Publish to dev.to
	devto_result = _publish_to_devto(article, devto_api_key)
	results.append(devto_result)

	# Update state if at least one platform succeeded
	if any(r.get("success") for r in results):
		state["date"] = today
		state["published"] = state.get("published", 0) + 1
		# Record before returning so a repeat can never slip through, even if a
		# later phase of the cycle fails.
		_record_publish(status, article)
		source = article.get("_source") or {}
		for result in results:
			if result.get("success"):
				result["source_url"] = source.get("url", "")
				result["source_title"] = source.get("title", "")
				if article.get("_followup_of") is not None:
					result["followup_of"] = article.get("_followup_title", "")

	return results


def _generate_article(llm: Any, status: dict) -> Optional[dict]:
	"""Write today's article: a deeper follow-up if one is earned, else a fresh take.

    Returns None when no fresh source is available or the LLM fails. Publishing
    nothing is correct here -- a static fallback article is what caused dozens of
    identical posts on dev.to.
    """
	if not llm:
		log.warning("[articles] no LLM available -- not publishing")
		return None

	# Prefer following up a post that readers actually showed up for. A proven
	# subject beats a cold trending guess, and the backlink compounds reach
	# across both posts.
	target = _followup_target(status, os.getenv("DEV_TO_API_KEY", "").strip())
	if target:
		log.info("[articles] following up %r (%d views)",
				 target.get("title", "")[:60], target.get("page_views", 0))
		followup = _generate_followup(llm, status, target)
		if followup:
			return followup
		# A failed follow-up must not cost the day's article.
		log.info("[articles] follow-up unusable -- falling back to a fresh source")

	source = _pick_source(status)
	if not source:
		log.warning("[articles] no fresh unused trending source found -- not publishing")
		return None

	log.info("[articles] source: %s (%s)", source.get("title", "")[:70], source.get("source"))

	prompt = (
		"Write your own substantially better article on the subject of this trending piece.\n\n"
		f"SOURCE TITLE: {source.get('title', '')}\n"
		f"SOURCE URL: {source.get('url', '')}\n"
		f"SOURCE PUBLISHER: {source.get('source', '')}\n"
		f"SOURCE SUMMARY: {source.get('summary', '') or '(no summary provided; rely on the title)'}\n\n"
		"Pick a specific practitioner angle on this subject. Add working code, "
		"tradeoffs, and failure modes the source does not cover. Do not reword the "
		"source. Your title must differ from the source title. Follow every "
		"formatting and source-handling rule in the system prompt, including the "
		"TITLE and TAGS rules. JSON only."
	)

	try:
		if hasattr(llm, "complete_json_for_role"):
			data = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=6000)
		else:
			data = llm.complete_json(prompt, system=_SYSTEM, max_tokens=6000)
	except Exception as exc:
		log.warning("[articles] LLM generation failed: %s -- not publishing", exc)
		return None

	if not (data.get("title") and data.get("body_markdown")):
		log.warning("[articles] LLM returned no usable article -- not publishing")
		return None

	article = _finalize(llm, data, source, status)
	if not article:
		return None

	if _too_similar_to_source(article, source):
		log.warning("[articles] output too close to source title -- not publishing")
		return None

	article["_source"] = source
	return article


def _finalize(llm: Any, data: dict, source: dict, status: dict) -> Optional[dict]:
	"""Run every quality gate shared by the fresh and follow-up paths.

    Kept as one function so the two paths cannot drift apart on fabrication,
    tone, title quality, or duplicate detection. Returns None to publish nothing.
    """
	# Normalize first: it deterministically fixes stray '#' headings and fence
	# artifacts, so we never spend free-tier LLM calls revising those.
	article = _normalize(data)

	# Drop invented spec tables before anything else looks at the body. This is
	# deterministic, so it costs no LLM call -- and asking the model to "fix"
	# numbers it hallucinated tends to produce different hallucinated numbers.
	article["body_markdown"], dropped = _strip_fabricated_tables(article["body_markdown"])
	if dropped:
		log.info("[articles] removed %d fabricated spec table(s)", dropped)

	# Fabrication is a correctness gate, not a formatting nit. If invented
	# figures survive table-stripping they are woven into prose, and no revision
	# reliably fixes that -- the model just invents different numbers. Check this
	# before spending a revision call, so a doomed article costs one call, not two.
	fabricated = _fabrication_problems(article["body_markdown"])
	if fabricated:
		log.warning("[articles] unverifiable claims in prose %s -- not publishing", fabricated)
		return None

	# The title decides whether the body is ever read, so a weak one is worth a
	# retry of its own. Retitling is one cheap call and does not touch the body.
	title_issues = _title_problems(article.get("title", ""))
	if title_issues:
		log.info("[articles] title issues %s -- requesting a better title", title_issues)
		better = _revise_title(llm, article, title_issues)
		if better:
			article["title"] = better
		else:
			log.warning("[articles] could not fix title %s -- not publishing", title_issues)
			return None

	problems = _format_problems(article["body_markdown"])
	if problems:
		log.info("[articles] format issues %s -- requesting revision", problems)
		revised = _revise_format(llm, article, problems)
		if revised:
			# Keep the vetted title: _revise_format may echo the pre-gate one.
			vetted_title = article.get("title", "")
			article = _normalize(revised)
			article["title"] = vetted_title
			article["body_markdown"], _ = _strip_fabricated_tables(article["body_markdown"])
			if _fabrication_problems(article["body_markdown"]):
				log.warning("[articles] revision introduced invented figures -- not publishing")
				return None

	article = _ensure_attribution(article, source)

	# Tags are dev.to's distribution mechanism, so this runs on every path.
	preferred = list(status.get("article_stats", {}).get("winning_tags", []))
	article["tags"] = _boost_tags(article.get("tags", []), preferred)

	dup = _duplicate_reason(article, status)
	if dup:
		log.warning("[articles] %s -- not publishing", dup)
		return None

	return article


def _revise_title(llm: Any, data: dict, problems: list[str]) -> Optional[str]:
	"""Ask for a stronger headline only. Returns the new title, or None.

    Body-only retries are wasteful when the headline is the problem, so this
    sends just the title and the article's opening for context.
    """
	body = str(data.get("body_markdown", ""))
	opening = " ".join(body.split()[:120])
	prompt = (
		"Rewrite ONLY the title of this article so it earns clicks in the dev.to feed.\n\n"
		f"Current title: {data.get('title', '')}\n"
		f"Problems with it: {'; '.join(problems)}\n\n"
		f"Article opening for context:\n{opening}\n\n"
		"Follow the TITLE rules in the system prompt exactly: "
		f"{_TITLE_MIN_CHARS}-{_TITLE_MAX_CHARS} characters, concrete, names a real "
		"technology or failure, no clickbait words, no exclamation marks, no "
		"ALL-CAPS, no colon-subtitle padding.\n\n"
		'Respond with ONLY this JSON: {"title": "..."}'
	)
	try:
		if hasattr(llm, "complete_json_for_role"):
			out = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=300)
		else:
			out = llm.complete_json(prompt, system=_SYSTEM, max_tokens=300)
	except Exception as exc:
		log.warning("[articles] title revision failed: %s", exc)
		return None

	candidate = str((out or {}).get("title", "")).strip()
	if not candidate:
		return None
	remaining = _title_problems(candidate)
	if remaining:
		log.info("[articles] revised title still weak %s", remaining)
		return None
	log.info("[articles] title improved: %r", candidate)
	return candidate


def _followup_target(status: dict, api_key: str) -> Optional[dict]:
	"""Pick a recent high-performing post worth a deeper second article.

    Returns None whenever there is nothing clearly worth following up, so the
    normal trending path runs instead. Stats are an optimisation: a dev.to
    outage or a quiet week must never stop the daily article.
    """
	overrides = status.get("_overrides", {})
	if overrides.get("skip_followup"):
		log.info("[articles] follow-up skipped by owner command")
		return None
	if not _FOLLOWUP_ENABLED:
		return None

	published = devto_stats.fetch_published(api_key)
	if not published:
		return None

	# Record the reach numbers regardless of whether we follow up -- this is the
	# only place the bot ever learns whether its articles are read.
	status["article_stats"] = devto_stats.summarize(published)
	status["article_stats"]["winning_tags"] = devto_stats.winning_tags(published)

	hist = _history(status)
	done = {i for i in hist.get("followed_up_ids", []) if i is not None}
	# 'force followup' drops the view threshold so the owner can follow up a
	# post that has not yet cleared it. The already-followed-up guard still
	# applies, so this cannot produce the same sequel twice.
	forced = bool(overrides.get("force_followup"))
	best = devto_stats.top_performer(
		published,
		within_hours=_FOLLOWUP_WINDOW_HOURS,
		min_views=1 if forced else _FOLLOWUP_MIN_VIEWS,
		exclude_ids=done,
	)
	if not best:
		log.info("[articles] no post cleared %d views in %dh -- writing a fresh take",
				 _FOLLOWUP_MIN_VIEWS, _FOLLOWUP_WINDOW_HOURS)
		return None
	return best


def _generate_followup(llm: Any, status: dict, target: dict) -> Optional[dict]:
	"""Write a deeper sequel to a post that earned views. None if unusable."""
	source = _source_for_followup(status, target)
	prompt = (
		"Write a follow-up article that goes deeper than my earlier post below.\n\n"
		f"MY EARLIER POST TITLE: {target.get('title', '')}\n"
		f"MY EARLIER POST URL: {target.get('url', '')}\n"
		f"MY EARLIER POST SUMMARY: {target.get('description', '') or '(none)'}\n"
		f"IT EARNED: {target.get('page_views', 0)} views, "
		f"{target.get('reactions', 0)} reactions, {target.get('comments', 0)} comments\n"
		f"TAGS THAT WORKED: {', '.join(target.get('tags', [])) or '(none)'}\n\n"
		f"ORIGINAL EXTERNAL SOURCE: {source.get('title', '')} — {source.get('url', '')}\n\n"
		"Readers showed up for this subject, so do not re-explain the basics. Go "
		"one level deeper: production edge cases, what is harder than it looks, "
		"what you would do differently, or the problem a reader hits right after "
		"the first post. Link my earlier post once, inline. Follow every rule in "
		"the system prompt, including the TITLE rules. JSON only."
	)

	try:
		if hasattr(llm, "complete_json_for_role"):
			data = llm.complete_json_for_role(
				"post", prompt, system=_FOLLOWUP_SYSTEM, max_tokens=6000)
		else:
			data = llm.complete_json(prompt, system=_FOLLOWUP_SYSTEM, max_tokens=6000)
	except Exception as exc:
		log.warning("[articles] follow-up generation failed: %s", exc)
		return None

	if not (data.get("title") and data.get("body_markdown")):
		log.warning("[articles] follow-up returned no usable article")
		return None

	article = _finalize(llm, data, source, status)
	if not article:
		return None

	# A sequel that repeats the parent's title is worthless for reach.
	if _titles_overlap(article.get("title", ""), target.get("title", "")):
		log.warning("[articles] follow-up title too close to the original -- discarding")
		return None

	article["_source"] = source
	article["_followup_of"] = target.get("id")
	article["_followup_title"] = target.get("title", "")
	# Guarantee the inline backlink even if the model dropped it.
	article = _ensure_backlink(article, target)
	return article


def _source_for_followup(status: dict, target: dict) -> dict:
	"""Best-known external source for the post being followed up.

    The follow-up still credits the original external article. We do not store a
    per-post source map, so fall back to the target itself; ``_ensure_attribution``
    then links the earlier post rather than inventing a citation.
    """
	return {
		"title": target.get("title", ""),
		"url": target.get("url", ""),
		"source": "dev.to",
		"summary": target.get("description", ""),
	}


def _titles_overlap(new_title: str, old_title: str, threshold: float = 0.7) -> bool:
	"""True when two titles are close enough to read as the same headline."""
	new_key = trending.normalize_title(new_title)
	old_key = trending.normalize_title(old_title)
	if not new_key or not old_key:
		return False
	if new_key == old_key:
		return True
	new_words, old_words = set(new_key.split()), set(old_key.split())
	if not new_words or not old_words:
		return False
	return len(new_words & old_words) / len(new_words | old_words) >= threshold


def _ensure_backlink(article: dict, target: dict) -> dict:
	"""Make sure the follow-up links the post it builds on."""
	body = str(article.get("body_markdown", ""))
	url = str(target.get("url", "")).strip()
	if not url or url in body:
		return article
	title = str(target.get("title", "")).strip() or "my earlier post"
	# Insert after the opening paragraph so it reads as context, not a footnote.
	marker = "\n\n## "
	idx = body.find(marker)
	note = (
		f"\n\nThis builds on [{title}]({url}). You do not need to read that first, "
		"but it covers the background this post assumes.\n"
	)
	if idx == -1:
		article["body_markdown"] = body.rstrip() + note
	else:
		article["body_markdown"] = body[:idx] + note + body[idx:]
	return article


def _pick_source(status: dict) -> Optional[dict]:
	"""Return the best trending candidate that has not been used before."""
	try:
		candidates = trending.fetch_candidates(
			max_age_hours=_SOURCE_MAX_AGE_HOURS, limit=40
		)
	except Exception as exc:
		log.warning("[articles] trending fetch failed: %s", exc)
		return None

	used_urls = set(_history(status).get("source_urls", []))
	used_titles = set(_history(status).get("source_titles", []))
	for item in candidates:
		url_key = trending._canonical_url(item.get("url", ""))
		title_key = trending.normalize_title(item.get("title", ""))
		if url_key and url_key in used_urls:
			continue
		if title_key and title_key in used_titles:
			continue

		# Paywalled feeds give us a two-sentence teaser, which is not enough to
		# write a genuinely better article from. Try the public mirror once.
		if trending.needs_unlock(item):
			item["summary"] = trending.unlock_summary(item)
			if trending.needs_unlock(item):
				log.info(
					"[articles] skipping locked source with thin summary: %s",
					item.get("title", "")[:60],
				)
				continue
		return item
	return None


def _history(status: dict) -> dict:
	"""Persistent record of what has already been sourced and published."""
	return status.setdefault("article_history", {})


def _record_publish(status: dict, article: dict) -> None:
	"""Remember this article so it can never be published twice."""
	hist = _history(status)
	source = article.get("_source") or {}

	for key, value in (
		("source_urls", trending._canonical_url(source.get("url", ""))),
		("source_titles", trending.normalize_title(source.get("title", ""))),
		("titles", trending.normalize_title(article.get("title", ""))),
	):
		if not value:
			continue
		entries = hist.setdefault(key, [])
		if value not in entries:
			entries.append(value)
		# Bound the history so status.json cannot grow without limit.
		del entries[:-_HISTORY_LIMIT]

	# Remember which post we already mined for a follow-up, so the same winner is
	# not followed up every cycle for as long as it stays the top performer.
	parent_id = article.get("_followup_of")
	if parent_id is not None:
		done = hist.setdefault("followed_up_ids", [])
		if parent_id not in done:
			done.append(parent_id)
		del done[:-_HISTORY_LIMIT]


def _duplicate_reason(article: dict, status: dict) -> str:
	"""Return a reason string if this article repeats an earlier one."""
	title_key = trending.normalize_title(article.get("title", ""))
	if not title_key:
		return "article has no usable title"

	hist = _history(status)
	if title_key in set(hist.get("titles", [])):
		return f"duplicate title already published: {article.get('title', '')!r}"

	# Catch near-duplicates that differ by a word or two.
	new_words = set(title_key.split())
	if len(new_words) >= 3:
		for old in hist.get("titles", []):
			old_words = set(old.split())
			if not old_words:
				continue
			overlap = len(new_words & old_words) / len(new_words | old_words)
			if overlap >= 0.8:
				return f"near-duplicate of earlier title ({overlap:.0%} overlap): {old!r}"
	return ""


def _too_similar_to_source(article: dict, source: dict) -> bool:
	"""Reject output whose title merely restates the source title."""
	new_key = trending.normalize_title(article.get("title", ""))
	src_key = trending.normalize_title(source.get("title", ""))
	if not new_key or not src_key:
		return False
	if new_key == src_key:
		return True
	new_words, src_words = set(new_key.split()), set(src_key.split())
	if not new_words or not src_words:
		return False
	return len(new_words & src_words) / len(new_words | src_words) >= 0.85


def _ensure_attribution(article: dict, source: dict) -> dict:
	"""Guarantee the source is credited even if the model skipped the section."""
	body = str(article.get("body_markdown", ""))
	url = str(source.get("url", "")).strip()
	if not url:
		return article
	if url in body:
		return article
	title = str(source.get("title", "")).strip() or "the original article"
	body = body.rstrip() + (
		"\n\n## Source\n\n"
		f"This article builds on [{title}]({url}), adding implementation detail "
		"and tradeoffs for practitioners.\n"
	)
	article["body_markdown"] = body
	return article


# Title patterns that suppress clicks on dev.to. These are not merely hype -- the
# audience here reads them as low-effort content-farm output and scrolls past.
_TITLE_BANNED = [
	(r"\bultimate\b", 'clickbait word "ultimate"'),
	(r"\bcomplete guide\b", 'overused "complete guide"'),
	(r"\beverything you (need|ever needed) to know\b", 'overused "everything you need to know"'),
	(r"\byou need to know\b", 'clickbait "you need to know"'),
	(r"\b(amazing|awesome|incredible|mind.blowing|insane|crazy)\b", "hype adjective"),
	(r"\b(secrets?|hacks?)\b", 'content-farm word "secrets/hacks"'),
	(r"\bdeep dive\b", 'overused "deep dive"'),
	(r"\btop \d+\b", 'listicle "top N"'),
	(r"\bmust.(know|read|have)\b", 'clickbait "must-know"'),
	(r"!", "exclamation mark"),
	("__SHOUTING__", "ALL-CAPS word"),
	(r"\b\d+\s*(things|ways|tips|tricks)\s+(you|to|that)\b", "generic listicle framing"),
]

# Vague nouns that make a title invisible in a feed. Flagged only when the title
# carries no concrete technical anchor at all.
_TITLE_VAGUE = (
	"better code", "best practices", "getting started", "introduction to",
	"a guide to", "an overview", "the basics", "explained simply", "made easy",
	"for beginners", "in 2024", "in 2025", "in 2026",
)


# Acronyms that are normal in a technical title. Blocking these would reject
# perfectly good headlines like "Why Your JSON Parser Is Slower Than It Looks",
# so only non-acronym all-caps words count as shouting.
_KNOWN_ACRONYMS = {
	"JSON", "HTTP", "HTTPS", "HTML", "CSS", "YAML", "TOML", "CSV", "XML", "SQL",
	"REST", "GRPC", "GRAPHQL", "JWT", "OAUTH", "SAML", "CORS", "CRUD", "ACID",
	"TCP", "UDP", "DNS", "SSH", "TLS", "SSL", "VPN", "CDN", "URL", "URI", "API",
	"SDK", "CLI", "GUI", "IDE", "CPU", "GPU", "RAM", "SSD", "OS", "VM", "AWS",
	"GCP", "SQLITE", "POSTGRES", "MYSQL", "REDIS", "NGINX", "LLM", "LLMS", "RAG",
	"GPT", "AI", "ML", "ETL", "CI", "CD", "TDD", "DDD", "MVC", "ORM", "UUID",
	"ASCII", "UTF", "REGEX", "WASM", "PDF", "OCR", "NPM", "PIP", "GIT", "AST",
	"IO", "FIFO", "LIFO", "RPC", "SSR", "SPA", "PWA", "DOM", "SEO", "MRR", "IDE",
}


def _shouted_words(text: str) -> list[str]:
	"""All-caps words that are not recognised acronyms."""
	return [
		word for word in re.findall(r"\b[A-Z]{2,}\b", text)
		if word.upper() not in _KNOWN_ACRONYMS
	]


def _title_problems(title: str) -> list[str]:
	"""Reject titles that will not earn a click.

    Views are decided in the feed, before anyone sees the body, so the title
    gets a gate of its own. Deterministic -- costs no LLM call.
    """
	text = str(title or "").strip()
	problems: list[str] = []
	if not text:
		return ["title is empty"]

	if len(text) > _TITLE_MAX_CHARS:
		problems.append(f"title too long ({len(text)} chars, max {_TITLE_MAX_CHARS})")
	if len(text) < _TITLE_MIN_CHARS:
		problems.append(f"title too short ({len(text)} chars, min {_TITLE_MIN_CHARS})")

	for pattern, label in _TITLE_BANNED:
		if pattern == "__SHOUTING__":
			if _shouted_words(text):
				problems.append(f"title has {label}")
			continue
		if re.search(pattern, text, re.IGNORECASE):
			problems.append(f"title has {label}")

	lowered = text.lower()
	vague = [phrase for phrase in _TITLE_VAGUE if phrase in lowered]
	if vague:
		problems.append(f"title uses vague filler: {vague[0]!r}")

	# A colon subtitle usually means the model padded a weak headline. Allow a
	# short prefix ("Postgres: ...") but reject two full clauses.
	if ":" in text:
		head, _, tail = text.partition(":")
		if len(head.split()) >= 3 and len(tail.split()) >= 4:
			problems.append("title padded with a colon subtitle; pick the sharper half")

	return problems


# Large dev.to tags that actually carry feed traffic. A post needs at least one
# of these or it is only discoverable by direct link.
_HIGH_TRAFFIC_TAGS = {
	"programming", "python", "javascript", "webdev", "ai", "devops", "tutorial",
	"beginners", "opensource", "react", "node", "typescript", "career",
	"productivity", "computerscience", "coding", "database", "docker", "aws",
	"security", "testing", "rust", "go", "linux", "git", "machinelearning",
	"datascience", "cloud", "performance", "architecture", "llm",
}


def _boost_tags(tags: list[str], preferred: list[str]) -> list[str]:
	"""Guarantee the post lands in at least one high-traffic tag.

    dev.to distributes almost entirely by tag. A technically perfect article
    tagged only with niche slugs reaches nobody, which is the single cheapest
    reach bug to fix. ``preferred`` comes from what has actually worked on this
    account, so the account's own history wins over the static list.
    """
	clean: list[str] = []
	for tag in tags:
		slug = re.sub(r"[^a-z0-9]", "", str(tag).lower())
		if slug and slug not in clean:
			clean.append(slug)

	if not any(t in _HIGH_TRAFFIC_TAGS for t in clean):
		# Prefer a tag proven on this account, else fall back to the broadest one.
		boost = next((t for t in preferred if t in _HIGH_TRAFFIC_TAGS), "programming")
		# Drop the weakest (last) tag rather than exceeding dev.to's 4-tag limit.
		clean = [boost] + clean[:3]
		log.info("[articles] added high-traffic tag %r for reach", boost)

	return clean[:4] or ["programming", "python"]


def _format_problems(body: str) -> list[str]:
	"""Return a list of formatting rule violations in the generated markdown."""
	problems: list[str] = []
	words = len(body.split())
	if words < _MIN_WORDS:
		problems.append(f"too short ({words} words, need {_MIN_WORDS}+)")
	if len(re.findall(r"^## ", body, re.MULTILINE)) < 4:
		problems.append("fewer than 4 '##' sections")
	if len(re.findall(r"^```\w+", body, re.MULTILINE)) < 2:
		problems.append("fewer than 2 language-tagged code blocks")
	if re.search(r"^# ", body, re.MULTILINE):
		problems.append("uses a top-level '#' heading")
	if "key takeaway" not in body.lower():
		problems.append("missing '## Key Takeaways' section")
	if re.search(r"^```\s*$", body, re.MULTILINE) and not re.search(r"^```\w+", body, re.MULTILINE):
		problems.append("code block missing language tag")
	if re.search(r"^(#{2,3} .*)\n+(#{2,3} )", body, re.MULTILINE):
		problems.append("stacked headings with no prose between them")
	problems.extend(_fabrication_problems(body))
	problems.extend(_tone_problems(body))
	return problems


# Phrases that read as hype, filler, or condescension. The owner asked for a
# clear, clean, friendly tone, and these are the specific tics that break it.
_TONE_PATTERNS = [
	(r"\bin today's (world|fast-paced)", "cliche opener \"in today's world\""),
	(r"\b(revolutionary|game.changing|cutting.edge|paradigm shift)\b", "hype language"),
	(r"\b(simply|just) (use|run|add|call|do|install)\b", "condescending \"simply/just\""),
	(r"\bobviously\b", "condescending \"obviously\""),
	(r"\b(utilize|utilise|leverage|commence|endeavour|endeavor)\b", "corporate jargon"),
	(r"\b(delve|dive) (in|into) the (world|realm)\b", "cliche \"dive into the world\""),
	(r"\bit is worth noting that\b", "filler phrase"),
	(r"\b(unleash|supercharge|turbocharge|skyrocket)\b", "marketing verb"),
	(r"!(\s|$)", "exclamation mark"),
]


def _tone_problems(body: str) -> list[str]:
	"""Flag writing that breaks the clear, friendly, jargon-free house style."""
	prose = _strip_code_blocks(body)
	found: list[str] = []
	for pattern, label in _TONE_PATTERNS:
		if re.search(pattern, prose, re.IGNORECASE) and label not in found:
			found.append(label)

	# Long average sentences read as dense no matter how good the content is.
	sentences = [s for s in re.split(r"[.!?]+\s", prose) if len(s.split()) > 2]
	if sentences:
		avg = sum(len(s.split()) for s in sentences) / len(sentences)
		if avg > 26:
			found.append(f"sentences too long (avg {avg:.0f} words, aim under 22)")
	return found


# Numbers the model has no way to know and reliably invents: latency figures,
# parameter counts, prices per token, context windows. Prose outside code blocks
# only -- real numbers inside code (timeouts, retries) are fine.
_FABRICATION_PATTERNS = [
	(r"\b\d+\s*[-‐-―~]?\s*\d*\s*ms\b", "invented latency figures (ms)"),
	(r"\b\d+(\.\d+)?\s*[BTM]\b(?=[^a-z])", "invented model parameter counts"),
	(r"\$\s?\d+(\.\d+)?\s*(/|per\s)", "invented pricing"),
	(r"\b\d+(\.\d+)?\s*(tokens?/s|tok/s|req/s|requests?/(sec|second))", "invented throughput"),
	(r"\b\d+\s*%\s*(faster|slower|cheaper|better|more accurate)", "invented benchmark deltas"),
]


def _strip_code_blocks(body: str) -> str:
	"""Remove fenced code and inline code so only prose claims are checked."""
	body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
	return re.sub(r"`[^`\n]*`", " ", body)


def _fabrication_problems(body: str) -> list[str]:
	"""Flag unverifiable numeric claims in prose and tables.

    The model cannot know current latency, pricing, or parameter counts, and
    stating them as fact is the fastest way to lose a technical reader.
    """
	prose = _strip_code_blocks(body)
	found: list[str] = []
	for pattern, label in _FABRICATION_PATTERNS:
		if re.search(pattern, prose, re.IGNORECASE) and label not in found:
			found.append(label)
	return found


def _strip_fabricated_tables(body: str) -> tuple[str, int]:
	"""Delete markdown tables containing invented specs. Returns (body, count).

    A spec table is the model's favourite way to fabricate: it reaches for
    latency, parameter counts, and prices to fill cells. Removing the table
    keeps the rest of a good article publishable, and costs no LLM call.
    """
	lines = body.split("\n")
	out: list[str] = []
	removed = 0
	i = 0
	while i < len(lines):
		# A table is a run of consecutive lines that all contain a pipe.
		if "|" in lines[i]:
			start = i
			while i < len(lines) and "|" in lines[i]:
				i += 1
			block = lines[start:i]
			# Two lines (header + separator) is the minimum real table.
			if len(block) >= 2 and _fabrication_problems("\n".join(block)):
				removed += 1
				while i < len(lines) and not lines[i].strip():
					i += 1
				# Leave exactly one blank line so the next block does not butt
				# against the previous heading or paragraph.
				if out and out[-1].strip() and i < len(lines):
					out.append("")
				continue
			out.extend(block)
			continue
		out.append(lines[i])
		i += 1
	return "\n".join(out), removed


def _revise_format(llm: Any, data: dict, problems: list[str]) -> Optional[dict]:
	"""Ask the model to fix specific formatting violations. Returns None on failure."""
	prompt = (
		"Revise this article to fix the listed formatting problems. "
		"Keep the technical content and voice; only restructure and expand as needed.\n\n"
		f"Problems: {'; '.join(problems)}\n\n"
		f"Title: {data.get('title', '')}\n\n"
		f"Current body:\n{data.get('body_markdown', '')}\n\n"
		"Return the same JSON schema with the corrected body_markdown."
	)
	try:
		if hasattr(llm, "complete_json_for_role"):
			revised = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=6000)
		else:
			revised = llm.complete_json(prompt, system=_SYSTEM, max_tokens=6000)
	except Exception as exc:
		log.warning("[articles] format revision failed: %s", exc)
		return None

	if not revised.get("body_markdown"):
		return None
	remaining = _format_problems(revised["body_markdown"])
	if len(remaining) < len(problems):
		log.info("[articles] revision improved format (%d -> %d issues)", len(problems), len(remaining))
		revised.setdefault("title", data.get("title", ""))
		revised.setdefault("description", data.get("description", ""))
		revised.setdefault("tags", data.get("tags", []))
		return revised
	return None


def _normalize(data: dict) -> dict:
	"""Clean up markdown artifacts that hurt rendering on dev.to."""
	body = str(data.get("body_markdown", ""))
	# Strip a stray wrapping code fence around the whole article.
	if body.lstrip().startswith("```markdown"):
		body = re.sub(r"^\s*```markdown\s*\n", "", body)
		body = re.sub(r"\n```\s*$", "", body)
	# dev.to renders the title itself, so a top-level '#' heading shows up as a
	# duplicate title. Demote any '# ' to '## '.
	body = re.sub(r"^# (?!#)", "## ", body, flags=re.MULTILINE)
	# Strip "1. "/"2) " numbering the model adds to headings. dev.to renders a
	# clean outline without it, and the numbers go stale if sections are reordered.
	body = re.sub(r"^(#{2,3} )\d+[.)]\s+", r"\1", body, flags=re.MULTILINE)
	# Collapse 3+ blank lines to 2, then guarantee one blank line on both sides of
	# every heading. Without the trailing one, dev.to runs the first paragraph
	# into the heading.
	body = re.sub(r"\n{4,}", "\n\n\n", body)
	body = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", body)
	body = re.sub(r"^(#{2,3} .*)\n(?!\n)(?=\S)", r"\1\n\n", body, flags=re.MULTILINE)
	data["body_markdown"] = body.strip()

	tags = [
		re.sub(r"[^a-z0-9]", "", str(t).lower())
		for t in (data.get("tags") or ["python", "automation"])
	]
	data["tags"] = [t for t in tags if t][:4] or ["python", "automation"]
	return data


def _publish_to_devto(article: dict, api_key: str) -> dict:
	"""Publish article to dev.to and return action result."""
	url = "https://dev.to/api/articles"
	headers = {
		"api-key": api_key,
		"Content-Type": "application/json",
	}
	payload = {
		"article": {
			"title": article.get("title", "Untitled")[:80],
			"body_markdown": article.get("body_markdown", ""),
			"description": article.get("description", "")[:150] or article.get("title", "")[:150],
			"published": True,
			"tags": article.get("tags", ["python", "automation"])[:4],
		}
	}
	
	try:
		resp = requests.post(url, headers=headers, json=payload, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		article_url = data.get("url", "")
		log.info("[articles] Published to dev.to: %s", article_url)
		return {
			"platform": "dev.to",
			"success": True,
			"title": article.get("title", "Untitled"),
			"url": article_url,
			# dev.to pays nothing. Publishing is reach, not revenue, so this
			# must stay 0.0 — a non-zero constant here fabricates earnings.
			# Real money is only ever the on-chain wallet balance.
			"estimated_usd": 0.0,
		}
	except Exception as exc:
		log.error("[articles] dev.to publish failed: %s", exc)
		return {
			"platform": "dev.to",
			"success": False,
			"error": str(exc)[:200],
			"estimated_usd": 0.0,
		}
