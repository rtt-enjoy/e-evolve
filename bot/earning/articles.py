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
    "You are a senior software engineer and AI practitioner writing for an audience of professional developers."
    " Your readers ship production systems daily — they are impatient with fluff,"
    " respect hard-won experience, and will stop reading the moment you waste their time.\n\n"
    "VOICE AND TONE:\n"
    "- Write as a practitioner talking to peers — direct, confident, occasionally dry.\n"
    "- First-person is fine but earn it: share a real decision, a real mistake, a real number.\n"
    "- No motivational language ('unlock the power of...', 'revolutionise your workflow').\n"
    "- No hedging ('you might want to consider...') — state opinions clearly.\n"
    "- Prefer precise nouns over adjectives: 'a 400ms p99 latency' beats 'slow response times'.\n"
    "- Contractions are fine. Jargon is fine when accurate; define it once if rare.\n"
    "- Vary article style: tutorial (step-by-step), opinion/hot-take, post-mortem/failure story,"
    " comparison (A vs B), reference/cheatsheet, or explainer. Match style to topic.\n\n"
    "Respond with ONLY a single JSON object.\n\n"
    "Schema:\n"
    '{\n'
    '  "title": "Specific, outcome-focused title — no clickbait, no vague superlatives",\n'
    '  "tags": ["tag1", "tag2", "tag3"],\n'
    '  "description": "One crisp sentence summarising the concrete takeaway. Under 155 chars.",\n'
    f'  "body_markdown": "Full article in Markdown. At least {_MIN_WORDS} words. Follow structure rules below."\n'
    '}\n\n'
    "body_markdown STRUCTURE RULES (follow exactly):\n"
    "1. Open with a 2-3 sentence hook: a concrete situation, surprising number, or sharp observation."
    " No heading. No 'In this article...'.\n"
    "2. Use ## (H2) for 4-6 major sections. Use ### (H3) for sub-points when the section warrants it.\n"
    "3. Every code example in a fenced block with language tag (```python, ```bash, ```yaml, ```json,"
    " ```typescript, ```sql, ```dockerfile, etc.).\n"
    "4. At least 3 code examples. Each must be >6 lines, production-realistic, copy-pasteable."
    " Add a single-line comment explaining the non-obvious parts — not every line.\n"
    "5. Bullet lists only for true parallel items (3+). Prose flows as paragraphs, not fragmented bullets.\n"
    "6. Bold (**text**) for: critical warnings, key terms on first use, important CLI flags. Sparingly.\n"
    "7. Include at least one concrete result, metric, or failure story — something that happened, with numbers.\n"
    "8. End with ## Key Takeaways: 3-5 tight bullet points, each one actionable or decision-relevant.\n"
    "9. Banned phrases: 'In this article', 'In conclusion', 'As you can see', 'It's worth noting',"
    " 'leverage', 'seamless', 'game-changer', 'cutting-edge', 'deep dive', 'robust solution'.\n"
    "10. Do NOT wrap the entire body in a code fence. Plain markdown only.\n\n"
    "Topic domains: Python, JavaScript/TypeScript, systems programming, AI/ML engineering,"
    " DevOps/infrastructure, databases, security, web development, open-source tooling,"
    " software architecture, career/engineering culture. Pick whichever domain fits the topic."
    " Ground every article in real implementation detail — not theory."
)

_TOPICS = [
    # AI / LLM Engineering
    "How I built a self-improving bot that earns money while I sleep",
    "Building autonomous AI agents with free LLM APIs — a practical guide",
    "Multi-provider LLM fallback in Python: never let your bot go dark",
    "Prompt engineering for code generation: what actually works in 2026",
    "Structuring LLM outputs as JSON: parsing strategies that don't break",
    "Claude Sonnet 4.6 vs Haiku 4.5: cost-performance tradeoffs for autonomous agents",
    "Agentic AI in 2026: patterns that survived contact with production",
    "Free LLM APIs in 2026: Groq, Anthropic, Gemini, OpenRouter compared",
    "RAG without a vector database: BM25 + reranking in pure Python",
    "Fine-tuning vs prompting: when each approach actually wins",
    "LLM evals that don't lie: building an honest benchmark for your use case",
    "Context window management for long-running AI agents",
    # Python
    "Python dataclasses vs dicts vs Pydantic: when each wins in production",
    "Exponential backoff in Python: the right way to retry API calls",
    "Building observable autonomous bots: logging strategies that scale",
    "Why I store my bot's state in a JSON file instead of a database",
    "AST-based code safety checks: letting LLMs edit your repo without breaking it",
    "Python subprocess tricks for running CLI tools from autonomous agents",
    "Self-healing code: how bots can detect and fix their own regressions",
    "Python typing in 2026: what's actually useful vs ceremony",
    "Async Python for I/O-heavy bots: avoiding the footguns",
    "Writing Python packages that are easy to test without mocks",
    # GitHub Actions / DevOps
    "GitHub Actions is a free cloud computer — 8 things you can automate for $0",
    "Cron jobs on GitHub Actions: gotchas and best practices in 2026",
    "How to version a bot that modifies its own source code safely",
    "GitHub Actions secrets management for multi-provider AI pipelines",
    "Docker layer caching that actually works in CI in 2026",
    "Deploying a Python service to a $5 VPS with zero downtime",
    "Monitoring a side project for free: uptime, alerts, logs",
    # Web / TypeScript / JavaScript
    "Building a real-time dashboard with plain WebSockets — no framework needed",
    "TypeScript strict mode in 2026: the settings that matter",
    "Next.js App Router vs Pages Router: a year in production, honest verdict",
    "Server-sent events vs WebSockets: when each is the right call",
    "Writing a REST API in pure Node.js — no Express, no bloat",
    # Databases / Storage
    "SQLite in production: the surprising cases where it's the right call",
    "PostgreSQL indexing mistakes I made and how I fixed them",
    "Redis as a job queue: simple patterns that actually hold up",
    "Choosing between S3, R2, and Backblaze for a side project in 2026",
    # Security
    "Secrets management for solo developers: what actually matters",
    "OWASP Top 10 for Python APIs: the ones that bite you first",
    "JWT vs session cookies: the decision nobody makes consciously enough",
    # Software Architecture / Career
    "The 5-file architecture: keeping side projects alive for years",
    "When to use a monorepo — and when it's just overhead",
    "Writing technical articles with AI assistance: a realistic breakdown",
    "How I use GitHub Actions as a personal cron platform for $0",
    "The economics of running a dev content bot: real numbers after 440 cycles",
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
            max_tokens=4000,
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
                          url=url, success=True, estimated_usd=0.0)
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
                          url=url, success=True, estimated_usd=0.0)
        except Exception as exc:
            last_exc = exc
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
    return Result(platform="medium", error=str(last_exc)[:200] if last_exc else "max retries exceeded")
