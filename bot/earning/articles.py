"""
Earning Module — Articles
Generates one developer article per cycle and publishes it.

Activates with: DEV_TO_API_KEY  and/or  MEDIUM_INTEGRATION_TOKEN
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests

from bot.utils import sanitize_tags

def _load_strategy() -> dict:
    try:
        return json.loads(Path("config/strategy.json").read_text())
    except Exception:
        return {}

_strategy  = _load_strategy().get("articles", {})
_MIN_WORDS = int(_strategy.get("min_words", 600))

log = logging.getLogger(__name__)

_SYSTEM = (
    "You are a skilled technical writer producing articles for software developers.\n"
    "Write genuinely useful, experience-based content — not generic listicles.\n\n"
    "Respond with ONLY a single JSON object.\n\n"
    "Schema:\n"
    '{\n'
    '  "title": "Compelling, specific article title",\n'
    '  "tags": ["tag1", "tag2", "tag3"],\n'
    '  "description": "SEO meta description, under 155 characters",\n'
    f'  "body_markdown": "Full article in Markdown. At least {_MIN_WORDS} words. Include code examples."\n'
    '}\n\n'
    "Topics: Python automation, GitHub Actions, AI/LLM agents, passive income via code,\n"
    "self-improving bots, Web3 Python. Write in first-person, experience-based style."
)

_TOPICS = [
    "How I built a self-improving bot that earns money while I sleep",
    "GitHub Actions is a free cloud computer — 8 things you can automate for $0",
    "5 Python automation strategies for passive income in 2025",
    "Building autonomous AI agents with free LLM APIs — a practical guide",
    "Zero-cost infrastructure for side projects: GitHub Actions deep dive",
    "How to make Python scripts improve themselves using LLMs",
    "Web3 automation with Python: from zero to daily NFT mints",
    "My bot posted 100 dev.to articles — here's what happened",
    "Rate limiting your GitHub Actions bot: lessons from 418 cycles",
    "Prompt engineering for code generation: what actually works",
    "Building a personal finance tracker that runs for free on GitHub",
    "How I use Groq's free API tier to power an autonomous agent",
    "Python dataclasses vs dicts: when each wins",
    "Structuring LLM outputs as JSON: parsing strategies that don't break",
    "Cron jobs on GitHub Actions: gotchas and best practices",
    "From idea to deployed bot in 30 minutes with Python and GitHub Actions",
    "Writing dev.to articles programmatically: the API guide nobody wrote",
    "How to version a bot that modifies its own source code",
    "Exponential backoff in Python: the right way to retry API calls",
    "Building observable bots: logging strategies for autonomous systems",
    "Why I store my bot's state in a JSON file instead of a database",
    "Testing Python code that calls external APIs without mocking everything",
    "AST-based code safety checks: letting LLMs edit your repo safely",
    "The economics of running a dev content bot: real numbers after 400 cycles",
]


@dataclass
class Result:
    platform: str
    title: str = ""
    url: str = ""
    success: bool = False
    error: Optional[str] = None
    error_type: Optional[str] = None
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

def _classify_gen_error(exc: Exception) -> str:
    s = str(exc).lower()
    if "timeout" in s or "timed out" in s:
        return "llm_timeout"
    if "json" in s or "parse" in s or "decode" in s or "assertionerror" in type(exc).__name__.lower():
        return "llm_json"
    if "quota" in s or "rate" in s or "429" in s or "limit" in s:
        return "llm_quota"
    return "unknown"


def _generate(llm: Any, status: dict) -> Optional[dict]:
    import hashlib
    n     = status.get("total_runs", 1)
    idx   = int(hashlib.md5(str(n).encode()).hexdigest(), 16) % len(_TOPICS)
    topic = _TOPICS[idx]
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
        error_type = _classify_gen_error(exc)
        log.error("[articles] Generation failed [%s]: %s", error_type, exc)
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
                    "tags":          sanitize_tags(article.get("tags", []), max_tags=4),
                    "description":   article.get("description", ""),
                }},
                timeout=30,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 60))
                log.warning("[articles] dev.to rate limited — sleeping %ds", retry_after)
                time.sleep(retry_after)
                continue
            if resp.status_code in (400, 401, 403, 422):
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
                time.sleep(5 * (attempt + 1))
            else:
                return Result(platform="dev.to", error=str(exc)[:200])
    return Result(platform="dev.to", error="max retries exceeded")


# ── Medium ────────────────────────────────────────────────────────────────────

def _post_medium(article: dict, token: str) -> Result:
    auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    last_exc: Optional[Exception] = None
    for attempt in range(3):
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
                    "tags":          sanitize_tags(article.get("tags", []), max_tags=5),
                },
                timeout=30,
            )
            if resp.status_code in (400, 401, 403):
                return Result(platform="medium",
                              error=f"HTTP {resp.status_code}: {resp.text[:150]}")
            resp.raise_for_status()
            url = resp.json()["data"].get("url", "https://medium.com")
            return Result(platform="medium", title=article["title"],
                          url=url, success=True, estimated_usd=0.02)
        except Exception as exc:
            last_exc = exc
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    return Result(platform="medium", error=str(last_exc)[:200] if last_exc else "max retries exceeded")
