"""
Earning Module -- Newsletter Digest (dev.to)

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


_SYSTEM = """\\
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
        log.debug("[newsletter] disabled in strategy config -- skipping")
        return []
    state["enabled"] = True

    api_key = os.getenv("DEV_TO_API_KEY", "").strip()
    if not api_key:
        log.debug("[newsletter] DEV_TO_API_KEY not set -- skipping")
        return []

    forced = bool(status.get("_overrides", {}).get("force_newsletter"))
    if not forced:
        waiting = hours_until_due(state, "published_at", int(cfg["min_interval_hours"]))
        if waiting > 0:
            log.info("[newsletter] next issue due in %.1fh -- skipping", waiting)
            return []
    else:
        log.info("[newsletter] cadence bypassed by 'force newsletter' command")

    if not llm:
        log.warning("[newsletter] no LLM available -- publishing nothing")
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
            "[newsletter] only %d fresh source(s), need %d -- publishing nothing",
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
        log.warning("[newsletter] LLM generation failed: %s -- publishing nothing", exc)
        return None

    if not (data.get("title") and data.get("body_markdown")):
        log.warning("[newsletter] LLM returned no usable digest -- publishing nothing")
        return None

    # Deterministic cleanup first, so no LLM call is spent on fixable artifacts.
    issue = devto.normalize(data)
    issue["body_markdown"], dropped = devto.strip_fabricated_tables(issue["body_markdown"])
    if dropped:
        log.info("[newsletter] removed %d fabricated spec table(s)", dropped)

    issue["body_markdown"] = _ensure_sources(issue["body_markdown"], items)

    problems = _digest_problems(issue["body_markdown"], items, cfg)
    if problems:
        log.warning("[newsletter] %s -- publishing nothing", "; ".join(problems))
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
    """Return the top unused trending candidates for this issue."""
    try:
        candidates = trending.fetch_candidates(
            max_age_hours=int(cfg["source_max_age_hours"]),
            limit=40,
            exclude_authors=devto.own_post_urls(status),
        )
    except Exception as exc:
        log.warning("[newsletter] trending fetch failed: %s", exc)
        return []

    hist = _history(status)
    used_urls = set(hist.get("source_urls", []))
    used_titles = set(hist.get("source_titles", []))

    picked: list[dict] = []
    for item in candidates:
        url_key = trending._canonical_url(item.get("url", ""))
        title_key = trending.normalize_title(item.get("title", ""))
        if url_key and url_key in used_urls:
            continue
        if title_key and title_key in used_titles:
            continue

        # Paywalled feeds give us a two-sentence teaser, which is not enough to
        # write a genuinely useful digest from. Try the public mirror once.
        if trending.needs_unlock(item):
            item["summary"] = trending.unlock_summary(item)
            if trending.needs_unlock(item):
                log.info(
                    "[newsletter] skipping locked source with thin summary: %s",
                    item.get("title", "")[:60],
                )
                continue

        picked.append(item)
        if len(picked) >= int(cfg["items_per_issue"]):
            break

    return picked


def _ensure_sources(body: str, items: list[dict]) -> str:
    """Guarantee each story has a source line in the digest body.

    The model is prompted to add `Source:` lines, but if it drops one the
    digest would lack attribution. This appends any missing lines deterministically.
    """
    for item in items:
        url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        if not url or not title:
            continue
        source_line = f"\n\nSource: [{title}]({url})"
        if source_line not in body:
            body += source_line
    return body


def _digest_problems(body: str, items: list[dict], cfg: dict) -> list[str]:
    """Return a list of formatting rule violations specific to digests."""
    problems: list[str] = []
    min_words = int(cfg.get("min_words", 500))
    words = len(body.split())
    if words < min_words:
        problems.append(f"too short ({words} words, need {min_words}+)")
    if len(items) < int(cfg.get("min_items", 4)):
        problems.append(f"too few items ({len(items)}, need {cfg['min_items']})")
    # Every story must have a source line in the body.
    for item in items:
        url = item.get("url", "")
        if url and f"]({url})" not in body:
            problems.append(f"missing source line for {item.get('title', '')[:50]}")
    return problems


def _history(status: dict) -> dict:
    """Persistent record of what has already been sourced and published."""
    return status.setdefault("newsletter_history", {})


def _record_issue(status: dict, items: list[dict], limit: int) -> None:
    """Remember these items so they can never be featured twice."""
    hist = _history(status)
    limit = int(limit)
    for item in items:
        url = trending._canonical_url(item.get("url", ""))
        title = trending.normalize_title(item.get("title", ""))
        if url:
            bounded_append(hist.setdefault("source_urls", []), url, limit)
        if title:
            bounded_append(hist.setdefault("source_titles", []), title, limit)


def _record_reject(status: dict, reason: str) -> None:
    """Persist why a cycle published nothing, and keep a running tally."""
    rec = status.setdefault("newsletter_rejects", {})
    rec["last_reason"] = reason
    from datetime import datetime, timezone
    rec["last_at"] = datetime.now(timezone.utc).isoformat()
    counts = rec.setdefault("counts", {})
    counts[reason] = int(counts.get(reason, 0)) + 1
    rec["total"] = int(rec.get("total", 0)) + 1