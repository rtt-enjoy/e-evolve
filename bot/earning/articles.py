"""
Earning Module — Articles (dev.to and Medium)
Generates and publishes technical articles to dev.to and Medium.

Activates with: DEV_TO_API_KEY, MEDIUM_INTEGRATION_TOKEN (optional)
"""
from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

import requests

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

_SYSTEM = """\
You are a senior engineer writing for a developer audience on dev.to.

Write a well-structured, practical article (900-1600 words) on Python, AI/LLMs,
GitHub Actions, automation, or SaaS.

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
- Use a markdown table when comparing 3+ options.
- Use bulleted lists for enumerations, but never more than 7 items.
- Bold key terms sparingly with **term**, at most a few per article.
- End with a `## Key Takeaways` section of 3-5 concrete bullets.

CONTENT RULES:
- Be technically accurate and specific. Real library names, real flags.
- Never invent benchmarks, pricing, citations, or version numbers you are unsure of.
- No promotional fluff, no income guarantees, no "revolutionary"/"game-changing".
- Write as a practitioner reporting what worked, not a marketer."""

_TOPICS = [
    "Building a multi-provider LLM fallback chain that never breaks",
    "Free-tier AI APIs that need no credit card, and what each is good for",
    "Python patterns for AI agent orchestration",
    "GitHub Actions as a free compute platform for scheduled AI jobs",
    "Running a useful AI service on nothing but free tiers",
    "Error handling patterns for production AI agents",
    "How to validate and repair LLM output before you ship it",
    "Cutting LLM costs by routing each task to the cheapest capable model",
]


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
        log.warning("[articles] No article generated")
        return []
    
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
    
    return results


def _generate_article(llm: Any, status: dict) -> Optional[dict]:
    """Generate an article using the LLM, or return a fallback."""
    run_count = status.get("total_runs", 0) or 0
    topic = _TOPICS[run_count % len(_TOPICS)]
    
    if llm:
        try:
            prompt = (
                f'Write a practical article about: "{topic}". '
                f"This is bot cycle #{run_count}. "
                "Make it useful for Python developers interested in AI and automation. "
                "Follow every formatting rule in the system prompt. JSON only."
            )
            if hasattr(llm, "complete_json_for_role"):
                data = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=6000)
            else:
                data = llm.complete_json(prompt, system=_SYSTEM, max_tokens=6000)

            if data.get("title") and data.get("body_markdown"):
                problems = _format_problems(data["body_markdown"])
                if problems:
                    log.info("[articles] format issues %s -- requesting revision", problems)
                    data = _revise_format(llm, data, problems) or data
                return _normalize(data)
        except Exception as exc:
            log.warning("[articles] LLM generation failed: %s", exc)

    # Fallback to deterministic article
    return _fallback_article(topic, status, "LLM unavailable")


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
    return problems


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


def _fallback_article(topic: str, status: dict, error_type: str) -> dict:
    """Return a useful deterministic article when LLM generation is unavailable."""
    run = int(status.get("total_runs", 0) or 0)
    title = "When Your Content Bot Hits an LLM Quota, Ship the Fallback"
    description = "A practical pattern for keeping automated publishing alive when your LLM provider runs out of quota."
    body = f"""A publishing bot that depends on one LLM provider has a boring failure mode: the workflow is green, but nothing gets published. I hit that during cycle #{run}. The dev.to key was present, the command was read, and the article module simply returned no action after generation failed with `{error_type}`.

That is the kind of failure that looks harmless in CI and expensive in a content pipeline. The fix is not more optimism. The fix is a fallback path that produces a plain, useful, bounded article without calling another model.

## The Failure Mode

Most automation code treats content generation and content publishing as one step. That is convenient until the generator fails after the scheduler, secrets, and publishing client have all done their jobs.

## Separate Generation From Delivery

The publishing client should not care whether an article came from an LLM, a template, or a human-reviewed draft. Give it a strict article object and keep the fallback close to the generation boundary.

## Make the Fallback Honest

A fallback article should not pretend it has fresh benchmarks, citations, or provider-specific pricing. It should explain the operational lesson in front of it.

## Key Takeaways

- Treat article generation and article publishing as separate failure domains.
- Return a fallback article when LLM generation fails instead of returning an empty action list.
- Keep fallback content honest: no invented benchmarks, prices, or citations.
- Record the original error type so a successful publish does not hide provider trouble.
- Prefer deterministic recovery for unattended workflows that are expected to produce public output.

## Next Steps

This fallback article is a temporary solution. The long-term strategy is to:

1. Implement a multi-LLM provider system that can switch automatically
2. Add a quota monitoring dashboard to track usage across providers
3. Create a content buffer that stores pre-generated articles for emergencies
"""
    return {
        "title": title,
        "description": description,
        "body_markdown": body,
        "tags": ["python", "automation", "devops", "ai"],
    }


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