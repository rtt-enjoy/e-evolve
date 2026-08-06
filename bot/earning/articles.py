"""
Earning Module — Articles (dev.to and Medium)
Generates and publishes technical articles to dev.to and Medium.

Activates with: DEV_TO_API_KEY, MEDIUM_INTEGRATION_TOKEN (optional)
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Optional

import requests

from . import trending

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

_SYSTEM = """\
You are a senior engineer writing for a developer audience on dev.to.

You are given a REAL trending technology article as source material. Write your
own substantially better article on the same subject.

Respond with ONLY a single JSON object.

Schema:
{
  "title": "specific, benefit-driven title (max 80 chars)",
  "description": "one-sentence summary (max 150 chars)",
  "body_markdown": "full article in markdown",
  "tags": ["python", "ai", "automation"]
}

FORMATTING RULES for body_markdown -- follow all of them:
- Open with a 2-3 sentence hook stating the concrete problem. No "In today's world".
- Use `##` for main sections and `###` for sub-points. Never use `#` (the title owns it).
- 4-7 `##` sections with descriptive, specific headings. Not "Introduction"/"Conclusion".
- Keep paragraphs to 2-4 sentences. Insert a blank line between every block.
- Include at least two fenced code blocks with an explicit language tag
  (```python, ```yaml, ```bash) and code that would actually run.
- Explain each code block in prose immediately before or after it.
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


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Main entry point for the articles earning module."""
    devto_api_key = os.getenv("DEV_TO_API_KEY", "").strip()
    medium_token = os.getenv("MEDIUM_INTEGRATION_TOKEN", "").strip()
    
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

    # Publish to Medium if token is available
    if medium_token:
        medium_result = _publish_to_medium(article, medium_token)
        results.append(medium_result)

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

    return results


def _generate_article(llm: Any, status: dict) -> Optional[dict]:
    """Write an improved take on a real trending article.

    Returns None when no fresh source is available or the LLM fails. Publishing
    nothing is correct here -- a static fallback article is what caused dozens of
    identical posts on dev.to.
    """
    if not llm:
        log.warning("[articles] no LLM available -- not publishing")
        return None

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
        "formatting and source-handling rule in the system prompt. JSON only."
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

    # Normalize first: it deterministically fixes stray '#' headings and fence
    # artifacts, so we never spend free-tier LLM calls revising those.
    article = _normalize(data)
    problems = _format_problems(article["body_markdown"])
    if problems:
        log.info("[articles] format issues %s -- requesting revision", problems)
        revised = _revise_format(llm, article, problems)
        if revised:
            article = _normalize(revised)
    article = _ensure_attribution(article, source)

    if _too_similar_to_source(article, source):
        log.warning("[articles] output too close to source title -- not publishing")
        return None

    dup = _duplicate_reason(article, status)
    if dup:
        log.warning("[articles] %s -- not publishing", dup)
        return None

    article["_source"] = source
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


def _format_problems(body: str) -> list[str]:
    """Return a list of formatting rule violations in the generated markdown."""
    problems: list[str] = []
    words = len(body.split())
    if words < 600:
        problems.append(f"too short ({words} words, need 900+)")
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
    problems.extend(_fabrication_problems(body))
    return problems


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
    # Collapse 3+ blank lines to 2; ensure headings have a blank line before them.
    body = re.sub(r"\n{4,}", "\n\n\n", body)
    body = re.sub(r"(?<!\n)\n(#{2,3} )", r"\n\n\1", body)
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
            "estimated_usd": 0.08,
        }
    except Exception as exc:
        log.error("[articles] dev.to publish failed: %s", exc)
        return {
            "platform": "dev.to",
            "success": False,
            "error": str(exc)[:200],
            "estimated_usd": 0.0,
        }


def _publish_to_medium(article: dict, integration_token: str) -> dict:
    """Publish article to Medium and return action result."""
    url = "https://api.medium.com/v1/users/me/posts"
    headers = {
        "Authorization": f"Bearer {integration_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "title": article.get("title", "Untitled"),
        "content": article.get("body_markdown", ""),
        "contentFormat": "markdown",
        "publishStatus": "public",
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 201:
            data = resp.json()
            article_url = data.get("url", "")
            log.info("[articles] Published to Medium: %s", article_url)
            return {
                "platform": "Medium",
                "success": True,
                "title": article.get("title", "Untitled"),
                "url": article_url,
                "estimated_usd": 0.07,
            }
        else:
            log.error("[articles] Medium publish failed: %s - %s", resp.status_code, resp.text)
            return {
                "platform": "Medium",
                "success": False,
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
                "estimated_usd": 0.0,
            }
    except Exception as exc:
        log.error("[articles] Medium publish failed: %s", exc)
        return {
            "platform": "Medium",
            "success": False,
            "error": str(exc)[:200],
            "estimated_usd": 0.0,
        }