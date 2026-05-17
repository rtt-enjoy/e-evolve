"""
Earning Module — Articles (dev.to)
Generates and publishes technical articles to dev.to.

Activates with: DEV_TO_API_KEY
"""
from __future__ import annotations

import logging
import os
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
You are a technical writer for a developer audience.

Write a short, practical article (600-1500 words) on Python, AI/LLMs, GitHub Actions, automation, or SaaS.

Respond with ONLY a single JSON object.

Schema:
{
  "title": "compelling title (max 80 chars)",
  "description": "one-sentence description (max 150 chars)",
  "body_markdown": "full article in markdown",
  "tags": ["python", "ai", "automation"]
}

Rules:
- Title should be specific and benefit-driven
- Include code snippets if relevant
- End with a clear takeaway or CTA
- Use 2-4 relevant tags
- No promotional fluff or income guarantees"""

_TOPICS = [
    "How to build a self-improving GitHub Actions bot",
    "Python patterns for AI agent orchestration",
    "Free LLM APIs for automation in 2025",
    "GitHub Actions as a free compute platform",
    "Building a multi-platform content pipeline with Python",
    "Error handling patterns for production AI agents",
    "Automating code reviews with free LLMs",
    "Setting up a self-hosting automation stack",
]


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Main entry point for the articles earning module."""
    api_key = os.getenv("DEV_TO_API_KEY", "").strip()
    if not api_key:
        log.debug("[articles] DEV_TO_API_KEY not set — skipping")
        return []

    # Check rate limiting
    state = status.setdefault("article_daily", {})
    last_date = state.get("date", "")
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date().isoformat()
    
    if last_date == today:
        published_today = state.get("published", 0)
        if published_today >= _MAX_ARTICLES_PER_CYCLE:
            log.info("[articles] Already published %d article(s) today — skipping", published_today)
            return []

    # Generate and publish
    article = _generate_article(llm, status)
    if not article:
        log.warning("[articles] No article generated")
        return []

    result = _publish(article, api_key)
    
    # Update state
    if result.get("success"):
        state["date"] = today
        state["published"] = state.get("published", 0) + 1
    
    return [result]


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
                "JSON only."
            )
            if hasattr(llm, "complete_json_for_role"):
                data = llm.complete_json_for_role("post", prompt, system=_SYSTEM, max_tokens=2000)
            else:
                data = llm.complete_json(prompt, system=_SYSTEM, max_tokens=2000)
            
            if data.get("title") and data.get("body_markdown"):
                return data
        except Exception as exc:
            log.warning("[articles] LLM generation failed: %s", exc)
    
    # Fallback to deterministic article
    return _fallback_article(topic, status, "LLM unavailable")


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


def _publish(article: dict, api_key: str) -> dict:
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
        log.info("[articles] Published: %s", article_url)
        return {
            "platform": "dev.to",
            "success": True,
            "title": article.get("title", "Untitled"),
            "url": article_url,
            "estimated_usd": 0.08,
        }
    except Exception as exc:
        log.error("[articles] Publish failed: %s", exc)
        return {
            "platform": "dev.to",
            "success": False,
            "error": str(exc)[:200],
            "estimated_usd": 0.0,
        }