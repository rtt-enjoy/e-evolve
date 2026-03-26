"""
Earning Module — Articles
Generates one developer article per cycle and publishes it.

Activates with: DEV_TO_API_KEY  and/or  MEDIUM_INTEGRATION_TOKEN
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests

log = logging.getLogger(__name__)

_SYSTEM = """\
You are a skilled technical writer producing articles for software developers.
Write genuinely useful, experience-based content — not generic listicles.

Respond with ONLY a single JSON object.

Schema:
{
  "title": "Compelling, specific article title",
  "tags": ["tag1", "tag2", "tag3"],
  "description": "SEO meta description, under 155 characters",
  "body_markdown": "Full article in Markdown. At least 600 words. Include code examples."
}

Topics: Python automation, GitHub Actions, AI/LLM agents, passive income via code,
self-improving bots, Web3 Python. Write in first-person, experience-based style."""

_TOPICS = [
    "How I built a self-improving bot that earns money while I sleep",
    "GitHub Actions is a free cloud computer — 8 things you can automate for $0",
    "5 Python automation strategies for passive income in 2025",
    "Building autonomous AI agents with free LLM APIs — a practical guide",
    "Zero-cost infrastructure for side projects: GitHub Actions deep dive",
    "How to make Python scripts improve themselves using LLMs",
    "Web3 automation with Python: from zero to daily NFT mints",
    "My bot posted 100 dev.to articles — here's what happened",
]


@dataclass
class Result:
    platform: str
    title: str = ""
    url: str = ""
    success: bool = False
    error: Optional[str] = None
    estimated_usd: float = 0.0


def run(llm: Any, status: dict[str, Any]) -> list[dict]:
    """Generate one article and publish to every active platform."""
    devto_key = os.getenv("DEV_TO_API_KEY", "").strip()
    medium_tok = os.getenv("MEDIUM_INTEGRATION_TOKEN", "").strip()

    if not devto_key and not medium_tok:
        return []

    article = _generate(llm, status)
    if not article:
        return []

    results: list[Result] = []
    if devto_key:
        results.append(_post_devto(article, devto_key))
    if medium_tok:
        results.append(_post_medium(article, medium_tok))

    for r in results:
        if r.success:
            log.info("[articles] Published on %s: %s", r.platform, r.url)
        else:
            log.warning("[articles] %s failed: %s", r.platform, r.error)

    return [vars(r) for r in results]


# ── Generation ────────────────────────────────────────────────────────────────

def _generate(llm: Any, status: dict) -> Optional[dict]:
    n     = status.get("total_runs", 1)
    topic = _TOPICS[n % len(_TOPICS)]
    try:
        art = llm.complete_json(
            f'Write a developer article about: "{topic}"\n'
            f"Context: bot cycle #{n}, active modules: {status.get('active_features',[])}.\n"
            "JSON only.",
            system=_SYSTEM,
            max_tokens=3000,
        )
        assert art.get("title") and art.get("body_markdown"), "missing title or body"
        log.info("[articles] Generated: %s", art["title"][:70])
        return art
    except Exception as exc:
        log.error("[articles] Generation failed: %s", exc)
        return None


# ── dev.to ────────────────────────────────────────────────────────────────────

def _post_devto(article: dict, api_key: str) -> Result:
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://dev.to/api/articles",
                headers={"api-key": api_key, "Content-Type": "application/json"},
                json={"article": {
                    "title":         article["title"],
                    "body_markdown": article["body_markdown"],
                    "published":     True,
                    "tags":          article.get("tags", [])[:4],
                    "description":   article.get("description", ""),
                }},
                timeout=30,
            )
            if resp.status_code in (400, 401, 403, 422):
                # These won't change on retry
                return Result(platform="dev.to",
                              error=f"HTTP {resp.status_code}: {resp.text[:150]}")
            resp.raise_for_status()
            url = resp.json().get("url", "https://dev.to")
            return Result(platform="dev.to", title=article["title"],
                          url=url, success=True, estimated_usd=0.05)
        except requests.HTTPError as exc:
            return Result(platform="dev.to",
                          error=f"HTTP {exc.response.status_code}: {exc.response.text[:100]}")
        except Exception as exc:
            if attempt < 2:
                time.sleep(3)
            else:
                return Result(platform="dev.to", error=str(exc)[:200])
    return Result(platform="dev.to", error="max retries exceeded")


# ── Medium ────────────────────────────────────────────────────────────────────

def _post_medium(article: dict, token: str) -> Result:
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        me  = requests.get("https://api.medium.com/v1/me", headers=auth, timeout=15)
        me.raise_for_status()
        uid = me.json()["data"]["id"]

        resp = requests.post(
            f"https://api.medium.com/v1/users/{uid}/posts",
            headers=auth,
            json={
                "title":         article["title"],
                "contentFormat": "markdown",
                "content":       f"# {article['title']}\n\n{article['body_markdown']}",
                "publishStatus": "public",
                "tags":          article.get("tags", [])[:5],
            },
            timeout=30,
        )
        resp.raise_for_status()
        url = resp.json()["data"].get("url", "https://medium.com")
        return Result(platform="medium", title=article["title"],
                      url=url, success=True, estimated_usd=0.02)
    except Exception as exc:
        return Result(platform="medium", error=str(exc)[:200])
